from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@override_settings(CACHES={"default": {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "browser-auth-tests",
}})
class BrowserAuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user("reader", password="ReadSecure!Pass82")

    def bootstrap(self, client=None):
        response = (client or self.client).get("/api/auth/session/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])
        return response.json()["csrfToken"]

    def login(self):
        csrf = self.bootstrap()
        response = self.client.post("/api/auth/session/login/", {
            "username": "reader", "password": "ReadSecure!Pass82",
        }, format="json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        self.csrf = response.json()["csrfToken"]
        return response

    def test_cookie_survives_new_client_without_exposing_bearer_token(self):
        response = self.login()
        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["max-age"], 30 * 24 * 60 * 60)
        self.assertEqual(cookie["path"], "/")
        self.assertFalse(cookie["domain"])
        self.assertNotIn("token", response.json())
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        reopened = APIClient(enforce_csrf_checks=True)
        reopened.cookies[settings.SESSION_COOKIE_NAME] = cookie.value
        self.assertEqual(reopened.get("/api/auth/session/").json()["username"], "reader")
        self.assertEqual(reopened.get("/api/review/streak/").status_code, 200)

    def test_login_rotates_session_key_and_csrf(self):
        old_csrf = self.bootstrap()
        old_key = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        response = self.login()
        self.assertNotEqual(response.cookies[settings.SESSION_COOKIE_NAME].value, old_key)
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        denied = self.client.post("/api/auth/session/logout/", HTTP_X_CSRFTOKEN=old_csrf)
        self.assertEqual(denied.status_code, 403)

    def test_login_signup_and_logout_require_csrf_even_when_anonymous(self):
        self.bootstrap()
        for path in ("login", "signup", "logout"):
            with self.subTest(path=path):
                response = self.client.post(f"/api/auth/session/{path}/", {}, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json()["code"], "csrf_failed")

    def test_cross_site_login_is_rejected_even_with_valid_csrf(self):
        csrf = self.bootstrap()
        response = self.client.post("/api/auth/session/login/", {
            "username": "reader", "password": "ReadSecure!Pass82",
        }, format="json", HTTP_X_CSRFTOKEN=csrf, HTTP_ORIGIN="https://attacker.example")
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(self.client.get("/api/auth/session/").json()["username"])

    def test_cookie_writes_require_csrf_and_logout_revokes_server_session(self):
        self.login()
        old_key = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        denied = self.client.post("/api/review/session/", {}, format="json")
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["code"], "csrf_failed")
        response = self.client.post("/api/auth/session/logout/", HTTP_X_CSRFTOKEN=self.csrf)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        replay = APIClient()
        replay.cookies[settings.SESSION_COOKIE_NAME] = old_key
        self.assertEqual(replay.get("/api/review/streak/").status_code, 401)

    def test_bad_password_preserves_current_session(self):
        self.login()
        response = self.client.post("/api/auth/session/login/", {
            "username": "reader", "password": "incorrect",
        }, format="json", HTTP_X_CSRFTOKEN=self.csrf)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.client.get("/api/auth/session/").json()["username"], "reader")

    def test_browser_auth_limits_repeated_password_attempts(self):
        csrf = self.bootstrap()
        for _ in range(10):
            response = self.client.post("/api/auth/session/login/", {
                "username": "reader", "password": "incorrect",
            }, format="json", HTTP_X_CSRFTOKEN=csrf)
            self.assertEqual(response.status_code, 401)
        response = self.client.post("/api/auth/session/login/", {
            "username": "reader", "password": "incorrect",
        }, format="json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 429)

    def test_expired_and_deleted_user_sessions_are_not_restored(self):
        self.login()
        key = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        Session.objects.filter(session_key=key).update(expire_date=timezone.now() - timedelta(seconds=1))
        self.assertIsNone(self.client.get("/api/auth/session/").json()["username"])
        self.login()
        self.user.delete()
        self.assertIsNone(self.client.get("/api/auth/session/").json()["username"])

    def test_signup_creates_cookie_session_without_token(self):
        csrf = self.bootstrap()
        response = self.client.post("/api/auth/session/signup/", {
            "username": "newreader", "password": "ReadSecure!Pass82", "password_confirm": "ReadSecure!Pass82",
        }, format="json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "newreader")
        self.assertNotIn("token", response.json())
        self.assertEqual(self.client.get("/api/review/streak/").status_code, 200)

    def test_account_deletion_clears_cookie_and_invalidates_session(self):
        self.login()
        key = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        response = self.client.delete("/api/auth/account/", {
            "password": "ReadSecure!Pass82",
        }, format="json", HTTP_X_CSRFTOKEN=self.csrf)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Session.objects.filter(session_key=key).exists())
        self.assertFalse(self.client.cookies[settings.SESSION_COOKIE_NAME].value)

    @override_settings(DEBUG=False, SESSION_COOKIE_NAME="__Host-ssd_session", SESSION_COOKIE_SECURE=True,
                       CSRF_TRUSTED_ORIGINS=["https://ssd-studyapp.vercel.app"])
    def test_production_cookie_flags_and_trusted_frontend_proxy(self):
        csrf = self.bootstrap()
        response = self.client.post("/api/auth/session/login/", {
            "username": "reader", "password": "ReadSecure!Pass82",
        }, format="json", HTTP_X_CSRFTOKEN=csrf, HTTP_ORIGIN="https://ssd-studyapp.vercel.app", secure=True)
        self.assertEqual(response.status_code, 200)
        cookie = response.cookies["__Host-ssd_session"]
        self.assertTrue(cookie["secure"])
        self.assertTrue(cookie["httponly"])
