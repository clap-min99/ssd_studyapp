from rest_framework.routers import DefaultRouter

from .views import DailyDigestViewSet, TermViewSet

router = DefaultRouter()
router.register("digests", DailyDigestViewSet, basename="digest")
router.register("terms", TermViewSet, basename="term")

urlpatterns = router.urls
