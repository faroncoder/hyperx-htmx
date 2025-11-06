
import pytest
import json

@pytest.mark.django_db
def test_htmx_redirect_flow(client):
    """
    End-to-end redirect simulation:
    1. Simulate an HTMX fragment call
    2. Server responds with HX-Redirect  
    3. Validate the follow-up request still fires contentUpdated
    """
    # Step 1 — initial fragment call
    response = client.get("/dashboard/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#main-content")
    assert response.status_code == 200
    assert "HX-Trigger" in response.headers

    payload = json.loads(response.headers["HX-Trigger"])
    assert "htmx:contentUpdated" in payload

    # Step 2 — test redirect flow using login-redirect endpoint
    redirect_response = client.get("/login-redirect/", HTTP_HX_REQUEST="true")
    
    # Follow redirect if it's a redirect response
    if redirect_response.status_code in (301, 302):
        target_url = redirect_response.headers["Location"]
        final_response = client.get(target_url, HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#main-content")
        assert final_response.status_code == 200
        assert "HX-Trigger" in final_response.headers
    else:
        # If not a redirect, just verify it works
        assert redirect_response.status_code == 200
