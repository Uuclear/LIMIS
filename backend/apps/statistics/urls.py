from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('test-volume/', views.TestVolumeView.as_view(), name='test-volume'),
    path('qualification-rate/', views.QualificationRateView.as_view(), name='qualification-rate'),
    path('strength-curve/', views.StrengthCurveView.as_view(), name='strength-curve'),
    path('cycle-analysis/', views.CycleAnalysisView.as_view(), name='cycle-analysis'),
    path('workload/', views.WorkloadView.as_view(), name='workload'),
    path('equipment-usage/', views.EquipmentUsageView.as_view(), name='equipment-usage'),
    path('tasks-by-project/', views.TaskByProjectView.as_view(), name='tasks-by-project'),
    path('tasks-by-method/', views.TaskByMethodView.as_view(), name='tasks-by-method'),
]
