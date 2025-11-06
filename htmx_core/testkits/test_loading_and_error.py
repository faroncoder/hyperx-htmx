import importlib
import pytest
from django.conf import settings
import json
from django.test import Client
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_htmx_loading_overlay(htmx_client):
    """HTMXLoadingMiddleware should inject spinner CSS."""
    resp = htmx_client.get("/test-loading/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#main-content")
    html = resp.content.decode()
    assert resp.status_code == 200
    assert ".htmx-loading" in html

@pytest.mark.django_db
def test_htmx_error_middleware(client):
    """HTMXErrorMiddleware should return friendly HTML on exception."""
    resp = client.get("/test-error/", HTTP_HX_REQUEST="true")
    html = resp.content.decode()
    assert resp.status_code == 500
    assert "alert-danger" in html
