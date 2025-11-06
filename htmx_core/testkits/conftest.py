import importlib
import pytest
from django.conf import settings
import json
from django.test import Client
from django.contrib.auth import get_user_model

# Override settings for tests to use proper URLs
@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Configure test-specific settings"""
    # Override URL configuration for tests
    settings.ROOT_URLCONF = 'htmx_core.testkits.urls'
    
    # Override HTMX redirect settings for tests
    settings.HTMX_REDIRECT_AUTH = "/dashboard/"
    settings.HTMX_REDIRECT_ANON = "/frontend/"
    
    # Configure HTMX protected endpoints for testing
    settings.HTMX_PROTECTED_ENDPOINTS = [
        r'^/acct/menu/',
        r'^/acct/ind/',
        r'^/acct/org/',
    ]



@pytest.fixture
def client_non_htmx(db):
    from django.test import Client
    from django.contrib.auth import get_user_model
    return Client()
 

@pytest.fixture(scope="session")
def live_server_url(live_server):
    from django.test import Client
    from django.contrib.auth import get_user_model
    # Gives playwright a base URL to Django's test server
    return live_server.url


@pytest.fixture
def htmx_client(db):
    """Reusable Django test client configured for HTMX requests."""
    from django.test import Client
    from django.contrib.auth import get_user_model
    client = Client()
    # automatically include HX-Request header for all requests
    client.defaults.update({"HTTP_HX_REQUEST": "true"})
    return client



@pytest.fixture
def admin_client(db, django_user_model):
    """Django test client logged in as admin user."""
    from django.test import Client
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
    client = Client()
    client.force_login(admin)
    return client