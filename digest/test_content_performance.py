import gzip
import json

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient

from digest.models import Article, DailyDigest, LearningItem, ReviewSession, Tag, Term
from digest.review_sessions import session_data


class CompactContentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.digest = DailyDigest.objects.create(date="2026-10-16", subject="test", raw_text="원문 전체" * 500)
        self.item = LearningItem.objects.create(digest=self.digest, position=1, heading="FTL", body="검색 가능한 본문",
            source_text="개념 원문" * 500, deep_dive="자세한 해설" * 500)
        self.article = Article.objects.create(digest=self.digest, position=1, title="news", category="ssd", deep_dive="article explanation")
        self.tag = Tag.objects.create(slug="nand", name="NAND", category="ssd")
        self.item.tags.add(self.tag)
        self.article.tags.add(self.tag)

    def test_compact_lists_preserve_search_text_without_heavy_fields(self):
        for url in ("/api/learning-items/?compact=1", "/api/tags/nand/learning-items/?compact=1"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data[0]["body"], self.item.body)
                self.assertNotIn("source_text", response.data[0])
                self.assertNotIn("deep_dive", response.data[0])
        full = self.client.get("/api/learning-items/")
        self.assertEqual(full.data[0]["deep_dive"], self.item.deep_dive)
        articles = self.client.get("/api/tags/nand/articles/?compact=1")
        self.assertNotIn("deep_dive", articles.data[0])

    def test_compact_digest_is_smaller_and_detail_keeps_original_available(self):
        full = self.client.get("/api/digests/latest/")
        compact = self.client.get("/api/digests/latest/?compact=1")
        self.assertEqual(compact.status_code, 200)
        self.assertLess(len(compact.content), len(full.content) / 4)
        self.assertNotIn("raw_text", compact.data)
        self.assertNotIn("deep_dive", compact.data["learning_items"][0])
        detail = self.client.get(f"/api/content/learning-item/{self.item.pk}/")
        self.assertEqual(detail.data["source_text"], self.item.source_text)
        self.assertEqual(detail.data["deep_dive"], self.item.deep_dive)
        self.assertNotIn("raw_text", detail.data)
        fallback = self.client.get(f"/api/content/article/{self.article.pk}/")
        self.assertEqual(fallback.data["raw_text"], self.digest.raw_text)
        self.assertEqual(self.client.get("/api/content/invalid/1/").status_code, 404)
        self.assertEqual(self.client.get("/api/content/article/99999/").status_code, 404)

    def test_gzip_response_preserves_json(self):
        response = self.client.get("/api/learning-items/", HTTP_ACCEPT_ENCODING="gzip")
        self.assertEqual(response["Content-Encoding"], "gzip")
        data = json.loads(gzip.decompress(response.content))
        self.assertEqual(data[0]["deep_dive"], self.item.deep_dive)
        self.assertIn("Accept-Encoding", response["Vary"])


class ReviewQueryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="reader")
        tag = Tag.objects.create(slug="nand", name="NAND", category="ssd")
        self.ids = []
        for i in range(25):
            term = Term.objects.create(term=f"Term {i:02}", meaning=f"Meaning {i}")
            term.tags.add(tag)
            self.ids.append(term.pk)
        session_data(self.user)  # Preferences creation is not part of the measured read.

    def test_query_count_is_constant_for_one_or_twenty_cards(self):
        counts = {}
        for mode in ("written", "choice"):
            for count in (1, 20):
                session = ReviewSession.objects.create(user=self.user, date=timezone.localdate(),
                    term_ids=self.ids[:count], new_term_ids=[], scope={}, mode=mode)
                with CaptureQueriesContext(connection) as queries:
                    data = session_data(self.user, session)
                counts[mode, count] = len(queries)
                for card in data["session"]["terms"]:
                    self.assertEqual(len(card["options"]), 1 if mode == "written" else 4)
                    self.assertEqual(len(card["options"]), len(set(card["options"])))
                    self.assertIn(card["meaning"], card["options"])
            self.assertEqual(counts[mode, 1], counts[mode, 20])
        self.assertLess(counts["written", 20], counts["choice", 20])
        self.assertLessEqual(counts["choice", 20], 6)
