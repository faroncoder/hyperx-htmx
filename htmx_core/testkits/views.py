"""
Test views for HTMX Core test suite
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

def dashboard(request):
    """Test dashboard view"""
    content = "<div id='main-content'>HTMX Fragment</div>"
    
    # Add HTMX-specific features if it's an HTMX request
    if request.headers.get('HX-Request') == 'true':
        # Return fragment with proper HTMX attributes
        return HttpResponse(content, content_type="text/html")
    else:
        # Return full page for non-HTMX requests
        return HttpResponse(f"""
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>{content}</body>
</html>
        """, content_type="text/html")

def acct_menu(request):
    """Account menu test view"""
    return HttpResponse("<div id='menu'>Account menu</div>", content_type="text/html")

def login_redirect(request):
    """Test view for redirect flow"""
    return HttpResponseRedirect('/dashboard/')

def trigger_error(request):
    """Test view that triggers an error"""
    raise Exception("Test error for middleware")

def test_home_view(request):
    """Test home page for security middleware redirects"""
    return HttpResponse("<h1>Test Home</h1>", content_type="text/html")

@require_http_methods(["GET", "POST"])
def test_fragment_view(request):
    """Test view that returns a fragment"""
    fragment_content = """
    <div id="test-fragment" hx-swap-oob="true">
        <h3>Updated Content</h3>
        <p>This content was updated via HTMX</p>
    </div>
    """
    
    response = HttpResponse(fragment_content, content_type="text/html")
    
    # Add test triggers
    response.htmx_trigger = ['testTrigger', 'fragmentUpdated']
    
    return response

def test_error(request):
    """Test view for error middleware testing"""
    if request.headers.get('HX-Request') == 'true':
        # Simulate an error in HTMX context
        raise ValueError("Test HTMX error")
    else:
        return HttpResponse("Regular error page", content_type="text/html")

def test_loading(request):
    """Test view for loading middleware"""
    import time
    time.sleep(0.1)  # Small delay to test loading states
    
    content = """
    <div class="test-content">
        <h3>Loaded Content</h3>
        <p>This took a moment to load</p>
    </div>
    """
    
    return HttpResponse(content, content_type="text/html")