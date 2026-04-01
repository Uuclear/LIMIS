from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('samples', views.SampleViewSet, basename='sample')
router.register('sample-groups', views.SampleGroupViewSet, basename='sample-group')

urlpatterns = [
    path(
        'samples/public/verify/<str:sample_no>/',
        views.PublicSampleVerifyView.as_view(),
        name='public-sample-verify',
    ),
    path(
        'samples/public/verify/pk/<int:pk>/',
        views.PublicSampleVerifyView.as_view(),
        name='public-sample-verify-pk',
    ),
    path('', include(router.urls)),
]
