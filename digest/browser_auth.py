from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle

from .authentication import BrowserSessionAuthentication
from .serializers import SignupSerializer


def csrf_failure(request, reason=""):
    response = JsonResponse({
        "code": "csrf_failed", "detail": "요청 검증에 실패했습니다. 다시 시도해 주세요.",
    }, status=403)
    response["Cache-Control"] = "no-store, private"
    return response


def session_data(request):
    return {
        "username": request.user.username if request.user.is_authenticated else None,
        "csrfToken": get_token(request),
    }


@method_decorator(never_cache, name="dispatch")
class BrowserSessionView(APIView):
    authentication_classes = [BrowserSessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(session_data(request))


@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_protect, name="dispatch")
class BrowserLoginView(APIView):
    # Anonymous login needs CSRF protection too; DRF's session check alone
    # only checks requests that already have an authenticated session.
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "browser_auth"

    def post(self, request):
        username, password = request.data.get("username"), request.data.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            return Response({"detail": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=400)
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=401)
        login(request, user)
        return Response(session_data(request))


@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_protect, name="dispatch")
class BrowserSignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "browser_auth"

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                user = serializer.save()
        except IntegrityError:
            return Response({"username": ["이미 사용 중인 아이디입니다."]}, status=400)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return Response(session_data(request), status=201)


@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_protect, name="dispatch")
class BrowserLogoutView(APIView):
    authentication_classes = [BrowserSessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(session_data(request))
