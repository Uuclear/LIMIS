from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('suppliers', views.SupplierViewSet, basename='supplier')
router.register('items', views.ConsumableViewSet, basename='consumable')
router.register('in-records', views.ConsumableInViewSet, basename='consumable-in')
router.register('out-records', views.ConsumableOutViewSet, basename='consumable-out')

urlpatterns = [
    path('', include(router.urls)),
]
