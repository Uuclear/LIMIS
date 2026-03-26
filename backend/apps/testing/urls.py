from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('categories', views.TestCategoryViewSet, basename='test-category')
router.register('methods', views.TestMethodViewSet, basename='test-method')
router.register('parameters', views.TestParameterViewSet, basename='test-parameter')
router.register('tasks', views.TestTaskViewSet, basename='test-task')
router.register('templates', views.RecordTemplateViewSet, basename='record-template')
router.register('records', views.OriginalRecordViewSet, basename='original-record')
router.register('results', views.TestResultViewSet, basename='test-result')
router.register('judgment-rules', views.JudgmentRuleViewSet, basename='judgment-rule')

urlpatterns = [
    path('', include(router.urls)),
]
