from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from digest.models import ConceptBookmark, DailyDigest, LearningItem


class ConceptBookmarkTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="reader", password="password")
        self.other = get_user_model().objects.create_user(username="other", password="password")
        digest = DailyDigest.objects.create(date="2026-10-15", subject="test", raw_text="source")
        self.item = LearningItem.objects.create(digest=digest, position=1, heading="FTL", body="mapping")
        self.url = f"/api/concept-bookmarks/{self.item.pk}/"

    def test_anonymous_cannot_read_or_change_bookmarks(self):
        for method, url in (("get", "/api/concept-bookmarks/"), ("put", self.url), ("delete", self.url)):
            with self.subTest(method=method):
                self.assertIn(getattr(self.client, method)(url).status_code, (401, 403))
        self.assertFalse(ConceptBookmark.objects.exists())

    def test_save_and_remove_are_idempotent_and_account_scoped(self):
        ConceptBookmark.objects.create(user=self.other, item=self.item)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get("/api/concept-bookmarks/").json(), [])
        for _ in range(2):
            self.assertEqual(self.client.put(self.url).status_code, 200)
        self.assertEqual(ConceptBookmark.objects.filter(user=self.user).count(), 1)
        self.assertEqual(self.client.get("/api/concept-bookmarks/").json(), [self.item.pk])
        for _ in range(2):
            self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertEqual(self.client.get("/api/concept-bookmarks/").json(), [])
        self.assertTrue(ConceptBookmark.objects.filter(user=self.other, item=self.item).exists())

    def test_missing_concept_cannot_be_saved(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.put("/api/concept-bookmarks/999999/").status_code, 404)
        self.assertFalse(ConceptBookmark.objects.exists())

    def test_deleting_user_or_concept_removes_bookmarks(self):
        ConceptBookmark.objects.create(user=self.user, item=self.item)
        ConceptBookmark.objects.create(user=self.other, item=self.item)
        self.user.delete()
        self.assertEqual(ConceptBookmark.objects.count(), 1)
        self.item.delete()
        self.assertFalse(ConceptBookmark.objects.exists())
