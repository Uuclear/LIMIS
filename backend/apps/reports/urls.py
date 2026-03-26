from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.ReportViewSet, basename='report')

distribution_router = DefaultRouter()
distribution_router.register(
    'distributions',
    views.ReportDistributionViewSet,
    basename='report-distribution',
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        '<int:report_pk>/',
        include(distribution_router.urls),
    ),
]
