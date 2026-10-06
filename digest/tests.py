import base64
import importlib
import json
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import SimpleTestCase, TestCase, TransactionTestCase
from rest_framework.test import APIClient

from digest.models import Article, DailyDigest, LearningItem, Tag
from digest.serializers import DailyDigestDetailSerializer
from fetcher.gemini_parser import parse_digest_with_gemini
from fetcher.gmail_client import _decode_body
from fetcher.source_order import order_from_source, source_offset


HEADINGS = [f"SSD {i}" for i in range(1, 4)] + [f"자동차 {i}" for i in range(1, 4)]


def mail_and_response(count=6, articles=True):
    learning = [dict(heading=h, body=f"설명 {h}", source_text=f"{h}\n설명 {h}") for h in HEADINGS[:count]]
    news = [dict(title=f"기사 {i}", category=cat, source_text=f"기사 {i}\n기사 본문 {i}")
            for i, cat in enumerate(("ssd", "automotive"), 1)] if articles else []
    raw = "\n\n".join(item["source_text"] for item in news + learning)
    # Simulate exactly the observed rotation, and reversed article output.
    response = dict(date="2026-10-06", articles=list(reversed(news)),
                    learning_items=learning[1:] + learning[:1], terms=[])
    mail = dict(date="2026-10-06", subject="[2026-10-06] SSD 데일리 브리핑", body=raw)
    return mail, response


def gemini_client(response):
    client = Mock()
    client.models.generate_content.return_value.text = json.dumps(response)
    return client


class SourceOrderTests(SimpleTestCase):
    def test_gmail_decode_preserves_order(self):
        mail, _ = mail_and_response()
        encoded = base64.urlsafe_b64encode(mail["body"].encode()).decode()
        payload = {"parts": [{"mimeType": "text/plain", "body": {"data": encoded}}]}
        self.assertEqual(_decode_body(payload), mail["body"])

    def test_gemini_rotation_restored_for_variable_counts(self):
        for count in (2, 3, 6):
            with self.subTest(count=count):
                mail, response = mail_and_response(count)
                with patch("fetcher.gemini_parser._get_client", return_value=gemini_client(response)):
                    parsed = parse_digest_with_gemini(mail["body"])
                self.assertEqual([item.heading for item in parsed.learning_items], HEADINGS[:count])
                self.assertEqual([item.title for item in parsed.articles], ["기사 1", "기사 2"])

    def test_whitespace_and_heading_fallback(self):
        self.assertEqual(source_offset("intro\n제목\r\n본문", "제목\n본문", ""), 6)
        self.assertEqual(source_offset("intro\n제목\n본문", "잘못된 추출", "제목"), 6)

    def test_ambiguous_missing_and_duplicate_sources_rejected(self):
        for raw, items in (
            ("다른 내용", [SimpleNamespace(heading="제목", source_text="")]),
            ("제목\n제목", [SimpleNamespace(heading="제목", source_text="")]),
            ("제목", [SimpleNamespace(heading="제목", source_text="")] * 2),
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                order_from_source(raw, items, "heading")


class DigestOrderTests(TestCase):
    def setUp(self):
        self.api = APIClient()

    def fetch(self, count=6, articles=True, **options):
        mail, response = mail_and_response(count, articles)
        with patch("digest.management.commands.fetch_digest.fetch_latest_digest", return_value=mail), \
             patch("fetcher.gemini_parser._get_client", return_value=gemini_client(response)), \
             patch("digest.management.commands.fetch_digest.explain_item", return_value="해설"):
            output = StringIO()
            call_command("fetch_digest", stdout=output, **options)
        return output.getvalue()

    def assert_feed(self, digest, count, article_count=2):
        for url in (f"/api/digests/{digest.pk}/", "/api/digests/latest/"):
            response = self.api.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual([x["heading"] for x in data["learning_items"]], HEADINGS[:count])
            self.assertEqual([x["position"] for x in data["learning_items"]], list(range(1, count + 1)))
            self.assertEqual([x["title"] for x in data["articles"]], [f"기사 {i}" for i in range(1, article_count + 1)])

    def test_six_mixed_category_items_and_articles_reach_api_in_source_order(self):
        output = self.fetch()
        self.assert_feed(DailyDigest.objects.get(), 6)
        self.assertIn("position=1: SSD 1", output)
        self.assertIn("position=6: 자동차 3", output)

    def test_two_and_three_items_without_articles(self):
        for count in (2, 3):
            with self.subTest(count=count):
                self.fetch(count, articles=False, force=True)
                self.assert_feed(DailyDigest.objects.get(), count, article_count=0)

    def test_force_replaces_positions_and_skip_preserves_existing_items(self):
        self.fetch()
        digest = DailyDigest.objects.get()
        old_ids = set(digest.learning_items.values_list("pk", flat=True))
        self.fetch(count=2)
        self.assert_feed(digest, 6)
        self.fetch(count=3, force=True)
        self.assert_feed(digest, 3)
        self.assertFalse(old_ids.intersection(digest.learning_items.values_list("pk", flat=True)))

    def test_invalid_force_parse_does_not_delete_existing_digest(self):
        self.fetch()
        mail, response = mail_and_response()
        response["learning_items"][0].update(heading="없는 항목", source_text="없는 원문")
        with patch("digest.management.commands.fetch_digest.fetch_latest_digest", return_value=mail), \
             patch("fetcher.gemini_parser._get_client", return_value=gemini_client(response)):
            with self.assertRaises(CommandError):
                call_command("fetch_digest", force=True, stdout=StringIO())
        self.assert_feed(DailyDigest.objects.get(), 6)

    def test_dry_run_does_not_write(self):
        self.fetch(dry_run=True)
        self.assertFalse(DailyDigest.objects.exists())

    def test_positions_override_insertion_and_pk_order_in_every_endpoint(self):
        digest = DailyDigest.objects.create(date="2026-10-06", subject="test", raw_text="")
        tag = Tag.objects.create(slug="ftl", name="FTL", category="ssd")
        for position in (3, 1, 2):
            li = LearningItem.objects.create(digest=digest, position=position, heading=HEADINGS[position - 1], body="body")
            article = Article.objects.create(digest=digest, position=position, title=f"기사 {position}", category="ssd")
            li.tags.add(tag)
            article.tags.add(tag)
        older = DailyDigest.objects.create(date="2026-10-05", subject="old", raw_text="")
        LearningItem.objects.create(digest=older, position=1, heading="old", body="old")
        self.assert_feed(digest, 3, article_count=3)
        self.assertEqual([x["position"] for x in DailyDigestDetailSerializer(digest).data["articles"]], [1, 2, 3])
        for url in ("/api/tags/ftl/articles/", "/api/tags/ftl/learning-items/", "/api/learning-items/"):
            response = self.api.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual([x["position"] for x in response.json()[:3]], [1, 2, 3])
        self.assertEqual(self.api.get(f"/api/digests/{older.pk}/").json()["learning_items"][0]["heading"], "old")
        for Model, kwargs in ((LearningItem, dict(heading="duplicate", body="")), (Article, dict(title="duplicate", category="ssd"))):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Model.objects.create(digest=digest, position=1, **kwargs)


class PositionMigrationTests(TransactionTestCase):
    def test_historical_rows_restored_without_deleting_content_or_relations(self):
        executor = MigrationExecutor(connection)
        before = [("digest", "0014_source_text")]
        after = [("digest", "0015_content_position")]
        executor.migrate(before)
        try:
            apps = executor.loader.project_state(before).apps
            Digest = apps.get_model("digest", "DailyDigest")
            Li = apps.get_model("digest", "LearningItem")
            News = apps.get_model("digest", "Article")
            TagModel = apps.get_model("digest", "Tag")
            digest = Digest.objects.create(date="2026-10-06", subject="old", raw_text="기사 1\n내용\n기사 2\n내용\nSSD 1\n설명\nSSD 2\n설명")
            tag = TagModel.objects.create(slug="ftl", name="FTL", category="ssd")
            first = Li.objects.create(digest=digest, heading="SSD 2", body="preserved", source_text="SSD 2\n설명", deep_dive="cached")
            first.tags.add(tag)
            second = Li.objects.create(digest=digest, heading="SSD 1", body="preserved")
            unknown = Li.objects.create(digest=digest, heading="unmatched", body="preserved")
            news2 = News.objects.create(digest=digest, title="기사 2", category="automotive")
            news1 = News.objects.create(digest=digest, title="기사 1", category="ssd")
            executor = MigrationExecutor(connection)
            executor.migrate(after)
            self.assertEqual(list(LearningItem.objects.filter(digest_id=digest.pk).values_list("pk", "position")), [(second.pk, 1), (first.pk, 2), (unknown.pk, 3)])
            self.assertEqual(list(Article.objects.filter(digest_id=digest.pk).values_list("pk", "position")), [(news1.pk, 1), (news2.pk, 2)])
            restored = LearningItem.objects.get(pk=first.pk)
            self.assertEqual(restored.body, "preserved")
            self.assertEqual(restored.deep_dive, "cached")
            self.assertEqual(list(restored.tags.values_list("slug", flat=True)), ["ftl"])
            # Re-running the data routine also yields the same explicit positions.
            migration = importlib.import_module("digest.migrations.0015_content_position")
            with connection.schema_editor() as editor:
                migration.populate_positions(executor.loader.project_state(after).apps, editor)
            self.assertEqual(LearningItem.objects.get(pk=first.pk).position, 2)
        finally:
            MigrationExecutor(connection).migrate(after)
