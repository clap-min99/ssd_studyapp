from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import DailyDigest, Term
from .serializers import (
    DailyDigestDetailSerializer,
    DailyDigestListSerializer,
    TermDetailSerializer,
    TermFamiliarityUpdateSerializer,
    TermSerializer,
)


class LoginView(APIView):
    """
    POST /api/auth/login/  { "username": "...", "password": "..." }
    -> { "token": "...", "username": "..." }

    회원가입 화면은 없다 — 계정은 Django admin에서 직접 만든다 (아는 사람만 쓰는 개인용 도구).
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # 로그인 자체는 인증 없이 접근 가능해야 하므로 비워둔다

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"detail": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=401)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})


class DailyDigestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/digests/            -> 타임라인용 목록 (가벼운 버전)
    GET /api/digests/{id}/       -> 상세 (기사/학습콘텐츠/용어 전부 포함)
    GET /api/digests/latest/     -> 가장 최근 다이제스트 (오늘의 피드용)
    """

    queryset = DailyDigest.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "latest":
            return DailyDigestDetailSerializer
        return DailyDigestListSerializer

    @action(detail=False, methods=["get"])
    def latest(self, request):
        digest = self.get_queryset().first()  # Meta.ordering = ["-date"]
        if digest is None:
            return Response({"detail": "아직 저장된 다이제스트가 없습니다."}, status=404)
        serializer = self.get_serializer(digest)
        return Response(serializer.data)


class TermViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,   # 자기 채점(familiarity 수정)을 위해 PATCH 허용. 생성/삭제는 막아둔다.
    viewsets.GenericViewSet,
):
    """
    GET   /api/terms/                      -> 전체 용어 사전
    GET   /api/terms/?familiarity=new      -> 익숙도로 필터링
    PATCH /api/terms/{id}/                 -> 자기 채점 결과 반영 (familiarity 변경) — 로그인 필요
    POST  /api/terms/{id}/check_answer/    -> 서술형 답변을 Gemini로 첨삭 — 로그인 필요
    """

    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # GET은 누구나, 나머지는 로그인 필요

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return TermFamiliarityUpdateSerializer
        if self.action == "retrieve":
            return TermDetailSerializer
        return TermSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        familiarity = self.request.query_params.get("familiarity")
        if familiarity:
            qs = qs.filter(familiarity=familiarity)
        return qs

    @action(detail=True, methods=["post"])
    def check_answer(self, request, pk=None):
        term = self.get_object()
        user_answer = request.data.get("answer", "").strip()

        if not user_answer:
            return Response({"detail": "answer 값이 비어있습니다."}, status=400)

        # 무거운 의존성(google-genai)은 이 액션을 쓸 때만 로드한다
        from fetcher.gemini_parser import check_term_answer

        try:
            result = check_term_answer(
                term=term.term,
                meaning=term.meaning,
                relevance=term.relevance,
                user_answer=user_answer,
            )
        except Exception as e:
            return Response(
                {"detail": f"AI 첨삭 중 오류가 발생했습니다: {e}"}, status=502
            )

        return Response(result)