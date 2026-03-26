from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('audits', views.InternalAuditViewSet, basename='internal-audit')
router.register('audit-findings', views.AuditFindingViewSet, basename='audit-finding')
router.register('corrective-actions', views.CorrectiveActionViewSet, basename='corrective-action')
router.register('reviews', views.ManagementReviewViewSet, basename='management-review')
router.register('review-decisions', views.ReviewDecisionViewSet, basename='review-decision')
router.register('nonconformities', views.NonConformityViewSet, basename='nonconformity')
router.register('complaints', views.ComplaintViewSet, basename='complaint')
router.register('proficiency-tests', views.ProficiencyTestViewSet, basename='proficiency-test')
router.register('supervisions', views.QualitySupervisionViewSet, basename='quality-supervision')

urlpatterns = [
    path('', include(router.urls)),
]
