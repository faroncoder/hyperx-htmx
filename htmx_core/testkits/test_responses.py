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
def test_htmx_fragment_wrap_contains_script(client):
    """HTMX fragments should contain clearing script."""
    resp = client.get("/dashboard/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#main-content")
    html = resp.content.decode()

    # Basic structure checks
    assert "<script>" in html, "Expected clearing script in HTMX fragment"
    assert "#main-content" in html, "Expected target selector in wrapper"
    assert "htmx:contentUpdated" in html, "Expected event trigger in script"

@pytest.mark.django_db
def test_regular_request_no_script(client):
    """Non-HTMX requests should NOT include clearing wrapper."""
    resp = client.get("/dashboard/")
    html = resp.content.decode()
    assert "<script>" not in html or "htmx:contentUpdated" not in html
