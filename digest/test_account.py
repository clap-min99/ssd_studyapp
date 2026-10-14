from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from digest.models import DailyActivity, DailyDigest, Insight, Question, ReviewRecord, Term


class DeleteAccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="leaving", password="MyCurrent!Pass82")
        self.other = get_user_model().objects.create_user(username="staying", password="Other!Pass82")
        self.token = Token.objects.create(user=self.user)
        self.other_token = Token.objects.create(user=self.other)
        self.digest = DailyDigest.objects.create(date="2026-10-14", subject="shared", raw_text="mail")
        self.term = Term.objects.create(term="NAND", first_seen_digest=self.digest)
        for user in (self.user, self.other):
            Insight.objects.create(user=user, digest=self.digest, text="personal")
            Question.objects.create(user=user, digest=self.digest, text="question")
            ReviewRecord.objects.create(user=user, term=self.term, next_review_date="2026-10-15")
            DailyActivity.objects.create(user=user, date="2026-10-14")

    def test_deletion_removes_only_own_account_and_records(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.delete("/api/auth/account/", {
            "password": "MyCurrent!Pass82", "user_id": self.other.pk,
        }, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.other.pk).exists())
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
        self.assertTrue(Token.objects.filter(key=self.other_token.key).exists())
        for model in (Insight, Question, ReviewRecord, DailyActivity):
            self.assertFalse(model.objects.filter(user_id=self.user.pk).exists())
            self.assertTrue(model.objects.filter(user=self.other).exists())
        self.assertTrue(DailyDigest.objects.filter(pk=self.digest.pk).exists())
        self.assertTrue(Term.objects.filter(pk=self.term.pk).exists())
        self.assertEqual(self.client.get("/api/review/streak/").status_code, 401)
        self.client.credentials()
        self.assertEqual(self.client.post("/api/auth/login/", {
            "username": "leaving", "password": "MyCurrent!Pass82",
        }).status_code, 401)

    def test_missing_or_wrong_password_preserves_account(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        for data in ({}, {"password": ""}, {"password": "wrong"}, {"password": ["bad"]}):
            with self.subTest(data=data):
                response = self.client.delete("/api/auth/account/", data, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())
                self.assertTrue(Insight.objects.filter(user=self.user).exists())
                self.assertTrue(Token.objects.filter(key=self.token.key).exists())

    def test_anonymous_cannot_delete_account(self):
        response = self.client.delete("/api/auth/account/", {"password": "MyCurrent!Pass82"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(get_user_model().objects.count(), 2)
