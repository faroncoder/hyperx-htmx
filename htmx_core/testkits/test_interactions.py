import importlib
import pytest
from django.conf import settings
import json
from django.test import Client
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_htmx_fragment_render(htmx_client):
    """HTMX request should return fragment with proper trigger header."""
    resp = htmx_client.get("/dashboard/", HTTP_HX_TARGET="#main-content")
    html = resp.content.decode()

    assert resp.status_code == 200
    assert "HX-Trigger" in resp.headers
    payload = json.loads(resp.headers["HX-Trigger"])
    assert "htmx:contentUpdated" in payload
    assert "HTMX Fragment" in html  # depends on your partial template


@pytest.mark.django_db
def test_htmx_redirect_flow(htmx_client):
    """Middleware should preserve HX headers on redirect."""
    resp = htmx_client.get("/login-redirect/", HTTP_HX_REQUEST="true")
    assert resp.status_code in (301, 302)
    # follow redirect
    redirected_url = resp.headers["Location"]
    redirected = htmx_client.get(redirected_url, HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#main-content")
    assert "HX-Trigger" in redirected.headers


@pytest.mark.django_db
def test_non_htmx_redirect_security(client):
    """Non-HTMX requests to protected routes should be redirected."""
    resp = client.get("/acct/menu/")
    assert resp.status_code in (301, 302)
    assert "Location" in resp.headers
