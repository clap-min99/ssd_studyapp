from django.contrib import admin

from .models import Article, DailyActivity, DailyDigest, Insight, LearningItem, Question, ReviewRecord, Term


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0


class LearningItemInline(admin.TabularInline):
    model = LearningItem
    extra = 0


class TermInline(admin.TabularInline):
    model = Term
    extra = 0
    fk_name = "first_seen_digest"


@admin.register(DailyDigest)
class DailyDigestAdmin(admin.ModelAdmin):
    list_display = ["date", "subject", "parsed_at"]
    inlines = [ArticleInline, LearningItemInline, TermInline]
    ordering = ["-date"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "digest"]
    list_filter = ["category", "digest"]
    search_fields = ["title", "summary", "insight"]


@admin.register(LearningItem)
class LearningItemAdmin(admin.ModelAdmin):
    list_display = ["heading", "digest"]
    search_fields = ["heading", "body"]


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ["term", "first_seen_digest"]
    search_fields = ["term", "meaning"]


@admin.register(ReviewRecord)
class ReviewRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "term", "familiarity", "next_review_date", "interval_days"]
    list_filter = ["familiarity", "user"]
    search_fields = ["term__term"]


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ["user", "digest", "updated_at"]
    search_fields = ["text"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["user", "digest", "resolved", "created_at"]
    list_filter = ["resolved", "user"]
    search_fields = ["text"]


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "date"]
    list_filter = ["user"]