from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.EquipmentViewSet, basename='equipment')

calibration_router = DefaultRouter()
calibration_router.register(
    'calibrations',
    views.CalibrationViewSet,
    basename='equipment-calibration',
)

period_check_router = DefaultRouter()
period_check_router.register(
    'period-checks',
    views.PeriodCheckViewSet,
    basename='equipment-period-check',
)

maintenance_router = DefaultRouter()
maintenance_router.register(
    'maintenances',
    views.MaintenanceViewSet,
    basename='equipment-maintenance',
)

usage_log_router = DefaultRouter()
usage_log_router.register(
    'usage-logs',
    views.EquipUsageLogViewSet,
    basename='equipment-usage-log',
)

nested_prefix = '<int:equipment_pk>/'

urlpatterns = [
    path('', include(router.urls)),
    path(nested_prefix, include(calibration_router.urls)),
    path(nested_prefix, include(period_check_router.urls)),
    path(nested_prefix, include(maintenance_router.urls)),
    path(nested_prefix, include(usage_log_router.urls)),
]
