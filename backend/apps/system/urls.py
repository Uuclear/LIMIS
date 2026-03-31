from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('roles', views.RoleViewSet, basename='role')
router.register('permissions', views.PermissionViewSet, basename='permission')
router.register('audit-logs', views.AuditLogViewSet, basename='auditlog')
router.register('notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
