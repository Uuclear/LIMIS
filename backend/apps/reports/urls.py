from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.ReportViewSet, basename='report')
template_router = DefaultRouter()
template_router.register('', views.ReportTemplateViewSet, basename='report-template')

distribution_router = DefaultRouter()
distribution_router.register(
    'distributions',
    views.ReportDistributionViewSet,
    basename='report-distribution',
)

urlpatterns = [
    path('templates/', include(template_router.urls)),
    path('', include(router.urls)),
    path(
        '<int:report_pk>/',
        include(distribution_router.urls),
    ),
]
