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
def test_htmx_request_header_detection(client):
    """Server should recognize HTMX requests via HX-Request header."""
    resp = client.get("/dashboard/", HTTP_HX_REQUEST="true")
    assert resp.status_code == 200

@pytest.mark.django_db
def test_htmx_trigger_header_present(client):
    """HTMX response should include HX-Trigger for contentUpdated."""
    resp = client.get("/dashboard/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#main-content")
    assert "HX-Trigger" in resp.headers

    payload = json.loads(resp.headers["HX-Trigger"])
    assert "htmx:contentUpdated" in payload
    assert payload["htmx:contentUpdated"] == True
    
    # Also check for contentUpdated
    assert "contentUpdated" in payload
    assert payload["contentUpdated"] == True
