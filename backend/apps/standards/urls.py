from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('standards', views.StandardViewSet, basename='standard')
router.register('validations', views.MethodValidationViewSet, basename='method-validation')

urlpatterns = [
    path('', include(router.urls)),
]
