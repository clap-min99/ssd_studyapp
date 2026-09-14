from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DailyDigestViewSet,
    DueReviewsView,
    LoginView,
    SubmitReviewAnswerView,
    TermViewSet,
)

router = DefaultRouter()
router.register("digests", DailyDigestViewSet, basename="digest")
router.register("terms", TermViewSet, basename="term")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("review/due/", DueReviewsView.as_view(), name="review-due"),
    path("review/<int:term_id>/answer/", SubmitReviewAnswerView.as_view(), name="review-answer"),
] + router.urls