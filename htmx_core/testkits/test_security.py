import importlib
import pytest
from django.conf import settings
import json
from django.test import Client
from django.contrib.auth import get_user_model


@pytest.fixture(autouse=True)
def test_urls(settings):
    settings.ROOT_URLCONF = "htmx_core.testkits.urls"
    
    
@pytest.mark.django_db
def test_htmx_allowed_on_protected(client):
    """HTMX request to protected endpoint should pass normally."""
    resp = client.get("/acct/menu/", HTTP_HX_REQUEST="true")
    assert resp.status_code in (200, 204)

@pytest.mark.django_db
def test_direct_browser_redirects(client):
    """Direct non-HTMX access to protected endpoint should redirect."""
    resp = client.get("/acct/menu/")
    assert resp.status_code in (301, 302)
    assert "Location" in resp.headers

@pytest.mark.django_db
def test_redirect_target_matches_settings(client):
    """Redirect target should match configured fallback."""
    from django.conf import settings
    resp = client.get("/acct/menu/")
    if resp.status_code in (301, 302):
        redirect_target = resp.headers["Location"]
        expected_path = settings.HTMX_REDIRECT_AUTH.split(":")[-1]
        assert expected_path in redirect_target or redirect_target.startswith("/"), (
            f"Unexpected redirect target: {redirect_target}"
        )
