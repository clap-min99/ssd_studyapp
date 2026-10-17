from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from digest.models import Article, DailyDigest, LearningItem, ReviewRecord, Term


@override_settings(CACHES={"default": {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "digest-calendar-tests",
}})
class DigestCalendarTests(TestCase):
    def setUp(self):
        self.days = [DailyDigest.objects.create(date=f"2026-10-{day:02d}", subject="일별 콘텐츠", raw_text="")
                     for day in range(1, 7)]
        Article.objects.create(digest=self.days[0], position=1, title="기사", category="ssd")
        LearningItem.objects.create(digest=self.days[1], position=1, heading="개념", body="본문")
        self.term = Term.objects.create(term="다시 나온 용어", meaning="뜻", first_seen_digest=self.days[2])
        self.term.appeared_in.add(self.days[3], self.days[4])
        self.new_term = Term.objects.create(term="처음 나온 용어", meaning="뜻", first_seen_digest=self.days[4])
        self.new_term.appeared_in.add(self.days[4])

    def test_dates_include_every_kind_of_content_once_and_exclude_empty_days(self):
        with self.assertNumQueries(1):
            response = self.client.get("/api/digests/dates/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": digest.id, "date": str(digest.date)} for digest in self.days[4::-1]])

    def test_latest_skips_an_empty_digest(self):
        response = self.client.get("/api/digests/latest/?compact=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.days[4].id)

    def test_selected_day_contains_repeated_and_legacy_terms_without_duplicates(self):
        for suffix in ("", "?compact=1"):
            for index, expected in [(2, [self.term.id]), (3, [self.term.id]), (4, [self.term.id, self.new_term.id])]:
                with self.subTest(suffix=suffix, day=index):
                    response = self.client.get(f"/api/digests/{self.days[index].id}/{suffix}")
                    self.assertEqual(response.status_code, 200)
                    self.assertCountEqual([term["id"] for term in response.json()["terms"]], expected)

    def test_repeated_term_keeps_review_state_private(self):
        user = get_user_model().objects.create_user(username="calendar-owner")
        other = get_user_model().objects.create_user(username="calendar-other")
        ReviewRecord.objects.create(user=user, term=self.term, familiarity="mastered", next_review_date="2026-10-20")
        client = APIClient()
        for account, familiarity in [(user, "mastered"), (other, "new")]:
            client.force_authenticate(account)
            response = client.get(f"/api/digests/{self.days[3].id}/?compact=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["terms"][0]["my_familiarity"], familiarity)

    def test_empty_calendar_and_latest_have_no_selectable_content(self):
        DailyDigest.objects.all().delete()
        DailyDigest.objects.create(date="2026-10-07", subject="비어 있음", raw_text="")
        self.assertEqual(self.client.get("/api/digests/dates/").json(), [])
        self.assertEqual(self.client.get("/api/digests/latest/").status_code, 404)
