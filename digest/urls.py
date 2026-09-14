from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DailyDigestViewSet, LoginView, TermViewSet

router = DefaultRouter()
router.register("digests", DailyDigestViewSet, basename="digest")
router.register("terms", TermViewSet, basename="term")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
] + router.urls