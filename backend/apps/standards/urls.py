from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
# 挂载在 api/v1/standards/ 下，此处用空前缀，避免 /standards/standards/ 重复路径
router.register('', views.StandardViewSet, basename='standard')
router.register('validations', views.MethodValidationViewSet, basename='method-validation')

urlpatterns = [
    path('', include(router.urls)),
]
