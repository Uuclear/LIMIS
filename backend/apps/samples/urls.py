from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('samples', views.SampleViewSet, basename='sample')
router.register('sample-groups', views.SampleGroupViewSet, basename='sample-group')

urlpatterns = [
    path('', include(router.urls)),
]
