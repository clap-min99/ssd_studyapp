from rest_framework import serializers

from .models import Article, DailyDigest, Insight, LearningItem, Question, ReviewRecord, Term, Tag


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
    """용어 사전 기본형. my_familiarity는 로그인한 사용자 기준 '내 복습 상태'다.

    Term 자체엔 더 이상 familiarity가 없다(사람마다 다르므로) — 로그인 상태면
    요청한 사용자의 ReviewRecord를 찾아서 붙여주고, 비로그인이면 null.
    """

    first_seen_date = serializers.DateField(
        source="first_seen_digest.date", read_only=True
    )
    my_familiarity = serializers.SerializerMethodField()

    class Meta:
        model = Term
        fields = [
            "id",
            "term",
            "meaning",
            "relevance",
            "first_seen_date",
            "my_familiarity",
        ]

    def get_my_familiarity(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        record = obj.review_records.filter(user=request.user).first()
        return record.familiarity if record else "new"


class TermDetailSerializer(TermSerializer):
    """용어 카드 클릭 시 뜨는 상세 팝업용 — 이 용어가 언급된 모든 다이제스트 목록 포함."""

    appeared_in = DigestSummarySerializer(many=True, read_only=True)

    class Meta(TermSerializer.Meta):
        fields = TermSerializer.Meta.fields + ["appeared_in"]


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


class DueTermSerializer(serializers.ModelSerializer):
    """오늘 복습할 카드 목록용 — 복습에 필요한 정보만 가볍게."""

    class Meta:
        model = Term
        fields = ["id", "term", "meaning", "relevance"]


class ReviewAnswerSerializer(serializers.Serializer):
    familiarity = serializers.ChoiceField(
        choices=[c[0] for c in ReviewRecord.FAMILIARITY_CHOICES]
    )


class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = ["id", "text", "updated_at"]


class QuestionSerializer(serializers.ModelSerializer):
    digest_date = serializers.DateField(source="digest.date", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "resolved", "created_at", "digest_date"]
        read_only_fields = ["created_at"]

# digest/serializers.py
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['slug', 'name', 'description', 'category', 'order']


class TagDetailSerializer(TagSerializer):
    """챕터 상세 페이지용 — 레슨 본문, 선행/다음 챕터 정보를 포함한다."""

    prerequisite_slug = serializers.SerializerMethodField()
    prerequisite_name = serializers.SerializerMethodField()
    next_slug = serializers.SerializerMethodField()
    next_name = serializers.SerializerMethodField()

    class Meta(TagSerializer.Meta):
        fields = TagSerializer.Meta.fields + [
            "lesson_body",
            "prerequisite_slug",
            "prerequisite_name",
            "next_slug",
            "next_name",
        ]

    def get_prerequisite_slug(self, obj):
        return obj.prerequisite.slug if obj.prerequisite else None

    def get_prerequisite_name(self, obj):
        return obj.prerequisite.name if obj.prerequisite else None

    def _next_chapter(self, obj):
        return obj.next_chapters.filter(order__gt=0).order_by("order").first()

    def get_next_slug(self, obj):
        next_chapter = self._next_chapter(obj)
        return next_chapter.slug if next_chapter else None

    def get_next_name(self, obj):
        next_chapter = self._next_chapter(obj)
        return next_chapter.name if next_chapter else None


class LearningItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningItem
        fields = ['id', 'heading', 'body']
        