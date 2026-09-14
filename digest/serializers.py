from rest_framework import serializers

from .models import Article, DailyDigest, LearningItem, Term


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "links", "summary", "insight", "category"]


class LearningItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningItem
        fields = ["id", "heading", "body"]


class DigestSummarySerializer(serializers.ModelSerializer):
    """다른 시리얼라이저 안에 중첩해서 쓰는 가벼운 다이제스트 요약 (id/날짜/제목만)."""

    class Meta:
        model = DailyDigest
        fields = ["id", "date", "subject"]


class TermSerializer(serializers.ModelSerializer):
    first_seen_date = serializers.DateField(
        source="first_seen_digest.date", read_only=True
    )

    class Meta:
        model = Term
        fields = [
            "id",
            "term",
            "meaning",
            "relevance",
            "familiarity",
            "first_seen_date",
        ]


class TermDetailSerializer(TermSerializer):
    """용어 카드 클릭 시 뜨는 상세 팝업용 — 이 용어가 언급된 모든 다이제스트 목록 포함."""

    appeared_in = DigestSummarySerializer(many=True, read_only=True)

    class Meta(TermSerializer.Meta):
        fields = TermSerializer.Meta.fields + ["appeared_in"]


class TermFamiliarityUpdateSerializer(serializers.ModelSerializer):
    """자기 채점 결과 반영 전용 — familiarity 외에는 이 경로로 수정 불가하게 제한한다."""

    class Meta:
        model = Term
        fields = ["id", "familiarity"]


class DailyDigestListSerializer(serializers.ModelSerializer):
    """타임라인처럼 목록으로 보여줄 때 쓰는 가벼운 버전 (하위 항목은 개수만)."""

    article_count = serializers.IntegerField(source="articles.count", read_only=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = DailyDigest
        fields = ["id", "date", "subject", "article_count", "categories"]

    def get_categories(self, obj):
        return sorted(set(obj.articles.values_list("category", flat=True)))


class DailyDigestDetailSerializer(serializers.ModelSerializer):
    """상세 화면(오늘의 피드 등)에서 쓰는, 하위 항목을 전부 포함한 버전."""

    articles = ArticleSerializer(many=True, read_only=True)
    learning_items = LearningItemSerializer(many=True, read_only=True)
    terms = TermSerializer(many=True, read_only=True, source="first_seen_terms")

    class Meta:
        model = DailyDigest
        fields = [
            "id",
            "date",
            "subject",
            "articles",
            "learning_items",
            "terms",
        ]