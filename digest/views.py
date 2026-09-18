from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, viewsets, generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyActivity, DailyDigest, Insight, Question, ReviewRecord, Term, Tag, Article, LearningItem
from .serializers import (
    DailyDigestDetailSerializer,
    DailyDigestListSerializer,
    DueTermSerializer,
    InsightSerializer,
    QuestionSerializer,
    ReviewAnswerSerializer,
    TermDetailSerializer,
    TermSerializer,
    TagSerializer,
    ArticleSerializer,
    LearningItemSerializer
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

    @action(detail=True, methods=["get", "put"], permission_classes=[IsAuthenticated])
    def insight(self, request, pk=None):
        """
        GET /api/digests/{id}/insight/  -> 내가 이 다이제스트에 남긴 생각 (없으면 빈 텍스트)
        PUT /api/digests/{id}/insight/  { "text": "..." } -> 저장(있으면 덮어쓰기)
        """
        digest = self.get_object()

        if request.method == "GET":
            obj = Insight.objects.filter(user=request.user, digest=digest).first()
            return Response({"text": obj.text if obj else ""})

        text = request.data.get("text", "").strip()
        obj, _ = Insight.objects.update_or_create(
            user=request.user, digest=digest, defaults={"text": text}
        )
        return Response(InsightSerializer(obj).data)

    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticated])
    def questions(self, request, pk=None):
        """
        GET  /api/digests/{id}/questions/  -> 내가 이 다이제스트에 남긴 질문 목록
        POST /api/digests/{id}/questions/  { "text": "..." } -> 새 질문 추가
        """
        digest = self.get_object()

        if request.method == "GET":
            qs = Question.objects.filter(user=request.user, digest=digest)
            return Response(QuestionSerializer(qs, many=True).data)

        text = request.data.get("text", "").strip()
        if not text:
            return Response({"detail": "text 값이 비어있습니다."}, status=400)
        q = Question.objects.create(user=request.user, digest=digest, text=text)
        return Response(QuestionSerializer(q).data, status=201)


class TermViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET /api/terms/                -> 전체 용어 사전 (로그인 시 my_familiarity 포함)
    GET /api/terms/{id}/           -> 상세 (관련 기사 목록 포함)
    POST /api/terms/{id}/check_answer/  -> 서술형 답변을 Gemini로 첨삭 — 로그인 필요

    자기 채점(familiarity)은 이제 여기가 아니라 /api/review/ 쪽에서 처리한다
    (유저별로 기록해야 해서 Term 자체를 수정하는 방식이 더 이상 맞지 않는다).
    """

    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TermDetailSerializer
        return TermSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
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


class DueReviewsView(APIView):
    """
    GET /api/review/due/ -> 로그인한 사용자가 오늘 복습해야 할 용어 목록

    "오늘 복습할 것"의 기준:
      - 한 번도 복습 기록이 없는 용어 (처음 보는 것) — 바로 대상
      - 기록이 있지만 next_review_date가 오늘 이하로 지난 것
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        reviewed = {
            r.term_id: r
            for r in ReviewRecord.objects.filter(user=request.user)
        }

        due_terms = [
            term
            for term in Term.objects.all()
            if term.id not in reviewed or reviewed[term.id].next_review_date <= today
        ]

        serializer = DueTermSerializer(due_terms, many=True)
        return Response(serializer.data)


class SubmitReviewAnswerView(APIView):
    """
    POST /api/review/{term_id}/answer/  { "familiarity": "new" | "familiar" | "mastered" }

    자기 채점 결과를 반영해서 이 사용자의 ReviewRecord를 갱신하고,
    간격 반복 규칙에 따라 다음 복습일을 계산해서 돌려준다.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, term_id):
        term = get_object_or_404(Term, id=term_id)

        serializer = ReviewAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        familiarity = serializer.validated_data["familiarity"]

        record, _ = ReviewRecord.objects.get_or_create(
            user=request.user,
            term=term,
            defaults={"next_review_date": timezone.localdate()},
        )
        record.apply_answer(familiarity)
        record.save()

        # 스트릭 계산용 — 오늘 활동했다는 사실을 기록 (이미 있으면 중복 생성 안 함)
        DailyActivity.objects.get_or_create(user=request.user, date=timezone.localdate())

        return Response(
            {
                "term_id": term.id,
                "familiarity": record.familiarity,
                "interval_days": record.interval_days,
                "next_review_date": record.next_review_date,
            }
        )


class QuestionViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET    /api/questions/                  -> 내가 남긴 질문 전체 (해결 여부 무관)
    GET    /api/questions/?resolved=false   -> 아직 안 푼 질문만
    PATCH  /api/questions/{id}/             { "resolved": true } -> 해결 체크
    DELETE /api/questions/{id}/

    본인이 만든 질문만 보이고 수정/삭제할 수 있다 (get_queryset에서 유저로 한정).
    """

    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Question.objects.filter(user=self.request.user)
        resolved = self.request.query_params.get("resolved")
        if resolved is not None:
            qs = qs.filter(resolved=resolved.lower() == "true")
        return qs


class StreakView(APIView):
    """
    GET /api/review/streak/ -> { "current_streak": N, "active_today": true/false }

    "오늘 아직 안 했어도 어제까지 이어져 있으면 스트릭은 안 끊긴 걸로 표시"하는
    일반적인 스트릭 앱 관례를 따른다 (오늘 활동 안 했다고 바로 0으로 보여주면
    앱을 열자마자 스트릭이 깨진 것처럼 보여서 김빠짐).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_dates = set(
            DailyActivity.objects.filter(user=request.user).values_list("date", flat=True)
        )
        today = timezone.localdate()
        active_today = today in active_dates

        cursor = today if active_today else today - timezone.timedelta(days=1)
        streak = 0
        while cursor in active_dates:
            streak += 1
            cursor -= timezone.timedelta(days=1)

        return Response({"current_streak": streak, "active_today": active_today})
    
class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

class TagArticlesView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        return Article.objects.filter(tags__slug=self.kwargs['slug']).order_by('-digest__date')

class TagLearningItemsView(generics.ListAPIView):
    serializer_class = LearningItemSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        return LearningItem.objects.filter(tags__slug=self.kwargs['slug']).order_by('-digest__date')

class LearningItemListView(generics.ListAPIView):
    queryset = LearningItem.objects.all().order_by('-digest__date')
    serializer_class = LearningItemSerializer
    permission_classes = [AllowAny]