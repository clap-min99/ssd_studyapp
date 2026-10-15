from django.urls import path
from rest_framework.routers import DefaultRouter
from .review_sessions import ReviewSessionView

from .views import (
    DailyDigestViewSet,
    DeepDiveView,
    DueReviewsView,
    LoginView,
    SignupView,
    AccountView,
    QuestionViewSet,
    StreakView,
    SubmitReviewAnswerView,
    LearningItemListView,
    TagArticlesView,
    TagListView,
    TagDetailView,
    TagTermsView,
    TermViewSet,
    TagLearningItemsView,
    ChapterLessonsView,
    LessonDetailView,
    ConceptBookmarkListView,
    ConceptBookmarkView,
)

router = DefaultRouter()
router.register("digests", DailyDigestViewSet, basename="digest")
router.register("terms", TermViewSet, basename="term")
router.register("questions", QuestionViewSet, basename="question")

urlpatterns = [
    path("concept-bookmarks/", ConceptBookmarkListView.as_view(), name="concept-bookmark-list"),
    path("concept-bookmarks/<int:pk>/", ConceptBookmarkView.as_view(), name="concept-bookmark"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/account/", AccountView.as_view(), name="account"),
    path("review/due/", DueReviewsView.as_view(), name="review-due"),
    path("review/session/", ReviewSessionView.as_view(), name="review-session"),
    path("review/streak/", StreakView.as_view(), name="review-streak"),
    path("review/<int:term_id>/answer/", SubmitReviewAnswerView.as_view(), name="review-answer"),
    path("tags/", TagListView.as_view(), name="tag-list"),                              # 추가
    path("tags/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
    path("tags/<slug:slug>/terms/", TagTermsView.as_view(), name="tag-terms"),
    path("tags/<slug:slug>/articles/", TagArticlesView.as_view(), name="tag-articles"),
    path("tags/<slug:slug>/lessons/", ChapterLessonsView.as_view(), name="chapter-lessons"),
    path("deep-dive/<str:kind>/<int:pk>/", DeepDiveView.as_view(), name="deep-dive"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("learning-items/", LearningItemListView.as_view(), name="learning-item-list"),# 추가
    path("tags/<slug:slug>/learning-items/", TagLearningItemsView.as_view(), name="tag-learning-items"),
] + router.urls
