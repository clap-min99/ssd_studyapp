from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DailyDigest, Term
from .serializers import (
    DailyDigestDetailSerializer,
    DailyDigestListSerializer,
    TermSerializer,
)


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


class TermViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/terms/                     -> 전체 용어 사전
    GET /api/terms/?familiarity=new     -> 익숙도로 필터링
    """

    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        familiarity = self.request.query_params.get("familiarity")
        if familiarity:
            qs = qs.filter(familiarity=familiarity)
        return qs
