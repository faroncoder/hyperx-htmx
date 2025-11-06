import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_view():
    """Test that dashboard view works correctly"""
    client = Client()
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert "Dashboard" in response.content.decode()


@pytest.mark.django_db  
def test_fragment_view_htmx():
    """Test fragment view with HTMX request"""
    client = Client()
    response = client.get("/test-fragment/", HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    assert "This content was updated via HTMX" in response.content.decode()


@pytest.mark.django_db
def test_home_view():
    """Test home view"""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Test Home" in response.content.decode()


@pytest.mark.django_db
def test_loading_view():
    """Test loading view"""
    client = Client()
    response = client.get("/test-loading/")
    assert response.status_code == 200
    assert "Loaded Content" in response.content.decode()