from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class SignupTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            "username": "newlearner",
            "password": "Study!Crane72Orbit",
            "password_confirm": "Study!Crane72Orbit",
        }

    def test_signup_returns_working_token_and_hashed_password(self):
        response = self.client.post("/api/auth/signup/", self.payload)
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username="newlearner")
        self.assertTrue(user.check_password(self.payload["password"]))
        self.assertNotEqual(user.password, self.payload["password"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(Token.objects.get(user=user).key, response.data["token"])
        self.assertNotIn("password", response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["token"]}')
        self.assertEqual(self.client.get("/api/review/streak/").status_code, 200)
        self.client.credentials()
        login = self.client.post("/api/auth/login/", self.payload)
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data["token"], response.data["token"])

    def test_invalid_signup_never_creates_user_or_token(self):
        invalid = [
            {"password_confirm": "different"},
            {"password": "12345678", "password_confirm": "12345678"},
            {"password": "short", "password_confirm": "short"},
            {"password": "newlearner", "password_confirm": "newlearner"},
            {"username": "invalid name"},
            {"username": ""},
            {"password": "", "password_confirm": ""},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                response = self.client.post("/api/auth/signup/", {**self.payload, **changes})
                self.assertEqual(response.status_code, 400)
                self.assertFalse(get_user_model().objects.exists())
                self.assertFalse(Token.objects.exists())
        response = self.client.post("/api/auth/signup/", {})
        self.assertEqual(response.status_code, 400)

    def test_duplicate_does_not_change_existing_credentials(self):
        user = get_user_model().objects.create_user(username="newlearner", password="Original!82Pass")
        response = self.client.post("/api/auth/signup/", self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
        user.refresh_from_db()
        self.assertTrue(user.check_password("Original!82Pass"))
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_client_cannot_grant_privileges(self):
        response = self.client.post("/api/auth/signup/", {
            **self.payload, "is_staff": True, "is_superuser": True,
        })
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
