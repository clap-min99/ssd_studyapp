from django.db import models


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
        DailyDigest, on_delete=models.SET_NULL, null=True, related_name="terms"
    )
    # 나중에 복습 화면에서 "얼마나 익숙한지" 표시하는 용도 (지금은 기본값만)
    familiarity = models.CharField(
        max_length=20,
        choices=[
            ("new", "처음 봄"),
            ("familiar", "익숙함"),
            ("mastered", "설명 가능"),
        ],
        default="new",
    )

    class Meta:
        ordering = ["term"]
        unique_together = ["term"]  # 같은 용어가 여러 날 반복 등장해도 하나만 유지

    def __str__(self) -> str:
        return self.term
