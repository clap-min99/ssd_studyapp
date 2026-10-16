from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from digest.models import Article, DailyDigest, ReviewRecord, Term


class ReadQueryPerformanceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="reader")
        self.other = get_user_model().objects.create_user(username="other")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.digest = DailyDigest.objects.create(date="2026-10-16", subject="test", raw_text="")
        self.term = Term.objects.create(term="FTL", meaning="mapping", first_seen_digest=self.digest)
        ReviewRecord.objects.create(user=self.user, term=self.term, familiarity="familiar", next_review_date=date.today())
        ReviewRecord.objects.create(user=self.other, term=self.term, familiarity="mastered", next_review_date=date.today())

    def read(self, path):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            data = response.json()
        return len(queries), data

    def test_term_list_queries_do_not_grow_with_terms(self):
        before, data = self.read("/api/terms/")
        self.assertEqual(data[0]["my_familiarity"], "familiar")
        self.assertEqual(data[0]["first_seen_date"], "2026-10-16")
        for i in range(12):
            Term.objects.create(term=f"NAND {i}", meaning="flash", first_seen_digest=self.digest)
        after, data = self.read("/api/terms/")
        self.assertEqual(after, before)
        self.assertEqual(len(data), 13)
        self.assertEqual(sum(t["my_familiarity"] == "new" for t in data), 12)

    def test_latest_queries_do_not_grow_with_terms(self):
        before, _ = self.read("/api/digests/latest/")
        for i in range(12):
            Term.objects.create(term=f"NAND {i}", meaning="flash", first_seen_digest=self.digest)
        after, data = self.read("/api/digests/latest/")
        self.assertEqual(after, before)
        self.assertEqual(len(data["terms"]), 13)

    def test_timeline_queries_do_not_grow_with_dates(self):
        Article.objects.create(digest=self.digest, position=1, title="news", category="ssd")
        before, _ = self.read("/api/digests/")
        for i in range(1, 10):
            digest = DailyDigest.objects.create(date=date(2026, 10, 16) - timedelta(days=i), subject="older", raw_text="")
            Article.objects.create(digest=digest, position=1, title="news", category="automotive")
        after, data = self.read("/api/digests/")
        self.assertEqual(after, before)
        self.assertEqual(data[0]["categories"], ["ssd"])
        self.assertEqual(data[1]["categories"], ["automotive"])
        self.assertTrue(all(d["article_count"] == 1 for d in data))
