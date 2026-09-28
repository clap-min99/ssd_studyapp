from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DailyDigestViewSet,
    DueReviewsView,
    LoginView,
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
)

router = DefaultRouter()
router.register("digests", DailyDigestViewSet, basename="digest")
router.register("terms", TermViewSet, basename="term")
router.register("questions", QuestionViewSet, basename="question")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("review/due/", DueReviewsView.as_view(), name="review-due"),
    path("review/streak/", StreakView.as_view(), name="review-streak"),
    path("review/<int:term_id>/answer/", SubmitReviewAnswerView.as_view(), name="review-answer"),
    path("tags/", TagListView.as_view(), name="tag-list"),                              # 추가
    path("tags/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
    path("tags/<slug:slug>/terms/", TagTermsView.as_view(), name="tag-terms"),
    path("tags/<slug:slug>/articles/", TagArticlesView.as_view(), name="tag-articles"),
    path("learning-items/", LearningItemListView.as_view(), name="learning-item-list"),# 추가
    path("tags/<slug:slug>/learning-items/", TagLearningItemsView.as_view(), name="tag-learning-items"),
] + router.urls