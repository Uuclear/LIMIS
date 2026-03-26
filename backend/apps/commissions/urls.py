from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.CommissionViewSet, basename='commission')

item_router = DefaultRouter()
item_router.register('items', views.CommissionItemViewSet, basename='commission-item')

review_router = DefaultRouter()
review_router.register(
    'contract-review',
    views.ContractReviewViewSet,
    basename='contract-review',
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        '<int:commission_pk>/',
        include(item_router.urls),
    ),
    path(
        '<int:commission_pk>/',
        include(review_router.urls),
    ),
]
