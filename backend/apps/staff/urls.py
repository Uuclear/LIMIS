from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('profiles', views.StaffProfileViewSet, basename='staff-profile')
router.register('certificates', views.CertificateViewSet, basename='certificate')
router.register('authorizations', views.AuthorizationViewSet, basename='authorization')
router.register('trainings', views.TrainingViewSet, basename='training')
router.register('evaluations', views.CompetencyEvalViewSet, basename='competency-eval')

urlpatterns = [
    path('', include(router.urls)),
]
