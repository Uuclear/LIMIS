from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('points', views.MonitoringPointViewSet, basename='monitoring-point')
router.register('records', views.EnvRecordViewSet, basename='env-record')
router.register('alarms', views.EnvAlarmViewSet, basename='env-alarm')

urlpatterns = [
    path('', include(router.urls)),
]
