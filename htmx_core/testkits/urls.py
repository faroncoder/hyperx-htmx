from django.urls import path, include
from . import views

# Frontend app URLs for security middleware
frontend_patterns = [
    path('', views.test_home_view, name='fronthome'),
]

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("acct/menu/", views.acct_menu, name="acct_menu"),
    path("login-redirect/", views.login_redirect, name="login_redirect"),
    path("trigger-error/", views.trigger_error, name="trigger_error"),
    path("test-fragment/", views.test_fragment_view, name="test_fragment"),
    path("test-error/", views.test_error, name="test_error"),
    path("test-loading/", views.test_loading, name="test_loading"),
    path("frontend/", include((frontend_patterns, 'frontend'), namespace='frontend')),
    path("", views.test_home_view, name="home"),  # Root fallback
]
