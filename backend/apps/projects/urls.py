from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.ProjectViewSet, basename='project')


def _nested_urls(viewset_cls, basename):
    r = DefaultRouter()
    r.register('', viewset_cls, basename=basename)
    return r.urls


urlpatterns = [
    path('', include(router.urls)),
    path(
        '<int:project_pk>/organizations/',
        include(_nested_urls(views.OrganizationViewSet, 'project-organization')),
    ),
    path(
        '<int:project_pk>/sub-projects/',
        include(_nested_urls(views.SubProjectViewSet, 'project-subproject')),
    ),
    path(
        '<int:project_pk>/contracts/',
        include(_nested_urls(views.ContractViewSet, 'project-contract')),
    ),
    path(
        '<int:project_pk>/witnesses/',
        include(_nested_urls(views.WitnessViewSet, 'project-witness')),
    ),
    path(
        '<int:project_pk>/samplers/',
        include(_nested_urls(views.SamplerViewSet, 'project-sampler')),
    ),
]
