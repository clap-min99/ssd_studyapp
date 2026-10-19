from django.utils.cache import patch_cache_control
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied


class PrivateAPICacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            patch_cache_control(response, private=True, no_store=True)
        return response


class BrowserSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        try:
            super().enforce_csrf(request)
        except PermissionDenied:
            raise PermissionDenied({
                "code": "csrf_failed",
                "detail": "요청 검증이 만료되었습니다. 다시 시도해 주세요.",
            })
