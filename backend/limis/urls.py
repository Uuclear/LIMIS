from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

api_v1_patterns = [
    path('system/', include('apps.system.urls')),
    path('projects/', include('apps.projects.urls')),
    path('commissions/', include('apps.commissions.urls')),
    path('samples/', include('apps.samples.urls')),
    path('testing/', include('apps.testing.urls')),
    path('reports/', include('apps.reports.urls')),
    path('equipment/', include('apps.equipment.urls')),
    path('staff/', include('apps.staff.urls')),
    path('environment/', include('apps.environment.urls')),
    path('standards/', include('apps.standards.urls')),
    path('quality/', include('apps.quality.urls')),
    path('consumables/', include('apps.consumables.urls')),
    path('statistics/', include('apps.statistics.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
