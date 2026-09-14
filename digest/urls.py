from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DailyDigestViewSet,
    DueReviewsView,
    LoginView,
    QuestionViewSet,
    StreakView,
    SubmitReviewAnswerView,
    TermViewSet,
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
] + router.urls