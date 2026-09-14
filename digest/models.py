from django.conf import settings
from django.db import models
from django.utils import timezone


class DailyDigest(models.Model):
    """다이제스트 메일 하나 = 이 모델 하나. Gmail에서 가져온 원문 전체를 보관."""

    date = models.DateField(unique=True)
    subject = models.CharField(max_length=255)
    raw_text = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.date} 다이제스트"


class Article(models.Model):
    """다이제스트 안의 기사 하나."""

    class Category(models.TextChoices):
        SSD = "ssd", "SSD/NAND"
        AUTOMOTIVE = "automotive", "자동차 SW"

    digest = models.ForeignKey(
        DailyDigest, on_delete=models.CASCADE, related_name="articles"
    )
    title = models.CharField(max_length=500)
    links = models.JSONField(default=list, blank=True)  # ["url1", "url2"]
    summary = models.TextField(blank=True)
    insight = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)

    class Meta:
        ordering = ["digest__date"]

    def __str__(self) -> str:
        return f"[{self.get_category_display()}] {self.title}"


class LearningItem(models.Model):
    """기사가 없는 날 오는 보충 학습 콘텐츠, 또는 기사와 별개로 오는 개념 설명."""

    digest = models.ForeignKey(
        DailyDigest, on_delete=models.CASCADE, related_name="learning_items"
    )
    heading = models.CharField(max_length=300)
    body = models.TextField()

    class Meta:
        ordering = ["digest__date"]

    def __str__(self) -> str:
        return self.heading


class Term(models.Model):
    """용어 사전. 처음 나온 다이제스트를 참조로 남겨서 출처를 추적한다."""

    term = models.CharField(max_length=200)
    meaning = models.TextField()
    relevance = models.TextField(blank=True)
    first_seen_digest = models.ForeignKey(
        DailyDigest, on_delete=models.SET_NULL, null=True, related_name="first_seen_terms"
    )
    # 같은 용어가 나중에 다시 나온 모든 다이제스트를 추적 (상세 팝업의 "관련 기사" 목록용)
    appeared_in = models.ManyToManyField(
        DailyDigest, related_name="mentioned_terms", blank=True
    )

    class Meta:
        ordering = ["term"]
        unique_together = ["term"]  # 같은 용어가 여러 날 반복 등장해도 하나만 유지

    def __str__(self) -> str:
        return self.term


class ReviewRecord(models.Model):
    """유저 한 명이 용어 하나를 복습한 상태. 간격 반복(spaced repetition)의 핵심 모델.

    familiarity는 더 이상 Term에 붙지 않는다 — 같은 용어라도 사람마다 익숙한 정도가
    다르기 때문에, "누가·어떤 용어를·다음에 언제 복습해야 하는지"를 여기서 따로 관리한다.
    """

    FAMILIARITY_CHOICES = [
        ("new", "몰랐음"),
        ("familiar", "애매함"),
        ("mastered", "알았음"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_records"
    )
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name="review_records"
    )
    familiarity = models.CharField(
        max_length=20, choices=FAMILIARITY_CHOICES, default="new"
    )
    interval_days = models.PositiveIntegerField(default=1)
    next_review_date = models.DateField()
    last_reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "term"]
        ordering = ["next_review_date"]

    def __str__(self) -> str:
        return f"{self.user} · {self.term} · 다음 복습 {self.next_review_date}"

    def apply_answer(self, familiarity: str) -> None:
        """자기 채점 결과를 반영해서 다음 간격을 계산한다 (단순 배수 방식).

        - 몰랐음  -> 내일 다시 (간격 1일로 리셋)
        - 애매함  -> 2일 뒤 (간격 2일로 리셋)
        - 알았음  -> 기존 간격을 2배로 늘림 (최소 2일)
        """
        if familiarity == "new":
            self.interval_days = 1
        elif familiarity == "familiar":
            self.interval_days = 2
        elif familiarity == "mastered":
            self.interval_days = max(self.interval_days * 2, 2)

        self.familiarity = familiarity
        self.next_review_date = timezone.localdate() + timezone.timedelta(
            days=self.interval_days
        )