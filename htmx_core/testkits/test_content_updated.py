import importlib
import pytest
from django.conf import settings
import json
from django.test import Client
from django.contrib.auth import get_user_model



@pytest.mark.django_db
def test_content_updated_trigger(htmx_client):
    """HX-Trigger payload structure should be valid JSON and contain details."""
    resp = htmx_client.get("/dashboard/", HTTP_HX_TARGET="#main-content")
    
    # Check that response is successful
    assert resp.status_code == 200
    
    # Check that HX-Trigger header is present
    assert "HX-Trigger" in resp.headers
    
    # Parse the trigger data
    data = json.loads(resp.headers["HX-Trigger"])
    
    # Check that contentUpdated trigger is present
    assert "contentUpdated" in data
    assert data["contentUpdated"] == True
    
    # Check for htmx:contentUpdated trigger as well
    assert "htmx:contentUpdated" in data
    assert data["htmx:contentUpdated"] == True
