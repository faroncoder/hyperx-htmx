"""
🚀 HyperX - HTMX's Sidekick ⚡
================================================================

TabX so fast! The ultimate HTMX enhancement protocol for Django.

MIT License - Copyright (c) 2025 Faron
https://github.com/yourusername/hyperx

HyperX provides a comprehensive HTMX integration system featuring:
- Lightning-fast TabX protocol (X-Tab system)  
- Attribute generation and parsing
- Security validation and authentication
- Response helpers and decorators
- Performance monitoring and logging

📖 TABLE OF CONTENTS
===================
1. Basic HTMX Attributes
2. TabX Protocol (Advanced X-Tab System)  
3. Form Handling
4. Authentication & Security
5. Response Helpers
6. Validation & Parsing
7. Performance & Debugging

════════════════════════════════════════════════════════════════════════════════
📝 1. BASIC HTMX ATTRIBUTES
════════════════════════════════════════════════════════════════════════════════

🔹 Simple Usage:
--------------
from core.utils.htmx_implemention import build_htmx_attrs

# Basic GET request
attrs = build_htmx_attrs(get='/api/data/', target='#content')

# With URL names (auto-reversed)  
attrs = build_htmx_attrs(get='api:user_data', target='#user-info')

# Multiple attributes
attrs = build_htmx_attrs(
    post='forms:submit',
    target='#form-container', 
    swap='outerHTML',
    trigger='submit'
)

🔹 In Templates:
---------------
<!-- Method 1: Direct attribute rendering -->
<button {% for attr in hx_attrs %}{{ attr.name }}="{{ attr.value }}"{% endfor %}>
    Load Data
</button>

<!-- Method 2: Custom template filter (recommended) -->
<button {{ hx_attrs|htmx_attrs }}>Load Data</button>

🔹 Event Handlers:
-----------------
attrs = build_htmx_attrs(
    get='api:refresh',
    target='#content',
    on_before_request='showLoader()',
    on_after_request='hideLoader()',
    on_response_error='handleError(event)'
)

════════════════════════════════════════════════════════════════════════════════
🎯 2. TABX PROTOCOL - Lightning Fast Tab Management ⚡
════════════════════════════════════════════════════════════════════════════════

🔹 TabX Generation (Lightning Fast!):
------------------------------------
# Create tabbed interface with version tracking - TabX so fast! ⚡
attrs = build_htmx_attrs(
    get='dashboard:profile',
    target='#tab-content', 
    xtab=('profile', 'load', 'view', '1.0')
)
# Generates HyperX header: X-Tab: "profile:1.0:load:view"

🔹 TabX Parsing in Views (HyperX Power!):
-----------------------------------------
from core.utils.htmx_implemention import parse_xtab_header

def profile_view(request):
    xtab = parse_xtab_header(request)
    if xtab:
        tab_name = xtab['tab']        # 'profile'
        version = xtab['version']     # '1.0'  
        function = xtab['function']   # 'load'
        command = xtab['command']     # 'view'
        
    return render(request, 'profile.html', {'tab_data': xtab})

🔹 TabX Validation Decorator (HyperX Security!):
------------------------------------------------
from core.utils.htmx_implemention import xtab_required

@xtab_required(expected_tab='profile', expected_function='load')
def secure_profile_view(request):
    # TabX automatically validated and parsed - so fast! ⚡
    xtab = request.xtab
    return JsonResponse({'loaded': xtab['tab']})

════════════════════════════════════════════════════════════════════════════════
📋 3. FORM HANDLING
════════════════════════════════════════════════════════════════════════════════

🔹 Form Submission Helper:
-------------------------
from core.utils.htmx_implemention import htmx_form_submit

# Standard form with loading states
form_attrs = htmx_form_submit(
    form_url='forms:contact_submit',
    target_id='#contact-form'
)

🔹 Advanced Form Configuration:
------------------------------
attrs = build_htmx_attrs(
    post='forms:ajax_submit',
    target='#form-results',
    swap='innerHTML',
    vals='{"csrf_token": "{{ csrf_token }}"}',
    headers='{"X-Requested-With": "XMLHttpRequest"}',
    on_before_request='lockForm()',
    on_after_request='unlockForm()'
)

🔹 Form Validation Response:
---------------------------
from core.utils.htmx_implemention import hx_trigger

def form_submit_view(request):
    if form.is_valid():
        form.save()
        return hx_trigger('form-saved', {'message': 'Saved successfully!'})
    else:
        return render(request, 'form_errors.html', {'form': form})

════════════════════════════════════════════════════════════════════════════════
🔐 4. AUTHENTICATION & SECURITY  
════════════════════════════════════════════════════════════════════════════════

🔹 HTMX-Aware Login Required:
----------------------------
from core.utils.htmx_implemention import htmx_login_required

@htmx_login_required
def protected_view(request):
    # For HTMX requests: shows login form inline
    # For regular requests: redirects to login page
    return render(request, 'protected_content.html')

🔹 Request Validation:
---------------------
from core.utils.htmx_implemention import validate_htmx_request

def api_view(request):
    if not validate_htmx_request(request):
        return HttpResponse('Invalid request', status=400)
        
    # Process valid HTMX request
    return JsonResponse({'data': 'secure'})

🔹 Security Headers:
-------------------
attrs = build_htmx_attrs(
    post='api:secure_endpoint',
    headers={
        'X-CSRFToken': '{{ csrf_token }}',
        'X-Requested-With': 'XMLHttpRequest',
        'Authorization': 'Bearer {{ user.auth_token }}'
    }
)

════════════════════════════════════════════════════════════════════════════════
🔄 5. RESPONSE HELPERS
════════════════════════════════════════════════════════════════════════════════

🔹 Redirects & Navigation:
-------------------------
from core.utils.htmx_implemention import (
    hx_redirect, hx_refresh, hx_location, 
    hx_push_url, hx_replace_url
)

def after_save_view(request):
    # HTMX redirect (no page reload)
    return hx_redirect('/dashboard/')
    
def refresh_view(request):
    # Force page refresh
    return hx_refresh()
    
def navigate_view(request):
    # Navigate with custom options
    return hx_location('/profile/', target='#main', swap='innerHTML')

🔹 URL History Management:
-------------------------
def update_history_view(request):
    # Add to browser history
    return hx_push_url('/new-page/')
    
def replace_history_view(request):  
    # Replace current history entry
    return hx_replace_url('/updated-page/')

🔹 Dynamic Retargeting:
----------------------
from core.utils.htmx_implemention import hx_retarget, hx_reswap

def conditional_view(request):
    if request.user.is_staff:
        # Target admin panel
        return hx_retarget('#admin-content')
    else:
        # Target user dashboard
        return hx_retarget('#user-content')

🔹 Event Triggering:
-------------------
from core.utils.htmx_implemention import hx_trigger

def notification_view(request):
    # Single event
    return hx_trigger('notification', {'message': 'Hello!'})
    
def multiple_events_view(request):
    # Multiple events
    events = {
        'notification': {'type': 'success', 'message': 'Saved!'},
        'analytics': {'action': 'form_submit', 'form_id': 'contact'},
        'ui-update': {'refresh_menu': True}
    }
    return hx_trigger(events)

════════════════════════════════════════════════════════════════════════════════
✅ 6. VALIDATION & PARSING
════════════════════════════════════════════════════════════════════════════════

🔹 HTMX Request Detection:
-------------------------
from core.utils.htmx_implemention import is_htmx_request, render_htmx

def flexible_view(request):
    if is_htmx_request(request):
        # Return partial template
        return render(request, 'partial.html', context)
    else:
        # Return full page
        return render(request, 'full_page.html', context)

🔹 Smart Template Rendering:
---------------------------
def auto_render_view(request):
    # Automatically chooses template based on request type
    return render_htmx(request, 'content.html', context)

🔹 X-Tab Validation:
-------------------
from core.utils.htmx_implemention import validate_xtab_request

def tab_handler_view(request):
    is_valid, xtab = validate_xtab_request(
        request, 
        expected_tab='dashboard',
        expected_function='refresh'
    )
    
    if not is_valid:
        return HttpResponse('Invalid tab request', status=400)
        
    # Process valid tab request
    return process_tab_action(xtab)

════════════════════════════════════════════════════════════════════════════════
📊 7. PERFORMANCE & DEBUGGING
════════════════════════════════════════════════════════════════════════════════

🔹 Logging Configuration (settings.py):
---------------------------------------
LOGGING = {
    'loggers': {
        'core.htmx_implementation.main': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'core.htmx_implementation.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
        },
        'core.htmx_implementation.performance': {
            'handlers': ['performance_file'], 
            'level': 'DEBUG',
        },
    }
}

🔹 Performance Monitoring:
-------------------------
# All functions automatically log performance metrics
# Check logs for timing and optimization opportunities

🔹 Debug Mode:
-------------
# Set logger level to DEBUG to see detailed attribute mapping
import logging
logging.getLogger('core.htmx_implementation.attrs').setLevel(logging.DEBUG)

════════════════════════════════════════════════════════════════════════════════
🎯 COMPLETE EXAMPLES
════════════════════════════════════════════════════════════════════════════════

🔹 Full Dashboard Example:
-------------------------
# views.py
from core.utils.htmx_implemention import *

@htmx_login_required
@xtab_required(expected_tab='dashboard')
def dashboard_view(request):
    # X-Tab data available in request.xtab
    tab_function = request.xtab['function']
    
    if tab_function == 'refresh':
        return render_htmx(request, 'dashboard/refresh.html', {
            'data': get_dashboard_data(),
            'refresh_attrs': build_htmx_attrs(
                get='dashboard:refresh',
                target='#dashboard-content',
                trigger='every 30s',
                xtab=('dashboard', 'refresh', 'auto', '1.1')
            )
        })
    
    return render_htmx(request, 'dashboard/main.html')

🔹 Interactive Form Example:
---------------------------
# Form with real-time validation
def contact_form_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return hx_trigger('form-success', {
                'message': 'Message sent!',
                'redirect_url': '/thank-you/'
            })
        else:
            # Return form with errors
            return render(request, 'contact_form.html', {
                'form': form,
                'submit_attrs': htmx_form_submit(
                    'contact:submit',
                    '#contact-form'
                )
            })
    
    # Initial form load
    form = ContactForm()
    return render(request, 'contact_form.html', {
        'form': form,
        'submit_attrs': htmx_form_submit('contact:submit', '#contact-form'),
        'validation_attrs': build_htmx_attrs(
            post='contact:validate',
            target='#validation-messages',
            trigger='keyup changed delay:500ms',
            swap='innerHTML'
        )
    })

════════════════════════════════════════════════════════════════════════════════
🛡️ SECURITY BEST PRACTICES
════════════════════════════════════════════════════════════════════════════════

✅ Always validate HTMX requests in sensitive views
✅ Use X-Tab validation for complex interfaces  
✅ Include CSRF tokens in form submissions
✅ Monitor security logs for unusual patterns
✅ Use htmx_login_required for protected views
✅ Validate expected targets in critical endpoints
✅ Log all X-Tab parsing for audit trails


    Build HTMX attributes list for template rendering
    
    Usage Examples:
    - hxs = build_htmx_attrs(get='/url/', trigger='load', target='#content')
    - hxs = build_htmx_attrs(request, post='accounts:login', target='#form')
    - hxs = build_htmx_attrs(get='core:dashboard', xtab=('profile', 'load', 'view', '1.0'))
    
    Args:
        request: Django request object (optional)
        get/post/put/delete: HTTP methods - supports URL names with ':'
        target: HTMX target selector
        swap: HTMX swap method
        trigger: HTMX trigger event
        headers: HTMX headers (JSON string or dict)
        push_url: Whether to push URL to history
        vals: HTMX values to include
        params: HTMX parameters
        xtab: X-Tab header tuple (tab_name, function, command, version)
        **kwargs: Additional attributes using snake_case -> hx-kebab-case

════════════════════════════════════════════════════════════════════════════════
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.urls import reverse
from functools import wraps
import json
import logging

# Comprehensive logging setup for HTMX implementation
logger_htmx_impl = logging.getLogger('core.htmx_implementation.main')
logger_htmx_attrs = logging.getLogger('core.htmx_implementation.attrs')
logger_htmx_forms = logging.getLogger('core.htmx_implementation.forms')
logger_htmx_validation = logging.getLogger('core.htmx_implementation.validation')
logger_htmx_auth = logging.getLogger('core.htmx_implementation.auth')
logger_htmx_security = logging.getLogger('core.htmx_implementation.security')
logger_htmx_performance = logging.getLogger('core.htmx_implementation.performance')



def build_htmx_attrs(request=None, get=None, post=None, put=None, delete=None,
                     target=None, swap=None, trigger=None, headers=None, 
                     push_url=None, vals=None, params=None, xtab=None, **kwargs):
   
    logger_htmx_attrs.debug(f"Building HTMX attributes: explicit params + {len(kwargs)} kwargs: {list(kwargs.keys())}")
    
    # Handle legacy calls where first parameter might be a kwarg instead of request
    if request is not None and isinstance(request, str):
        # Legacy call: build_htmx_attrs('/url/', other='value')
        # Shift parameters - assume it's a 'get' URL
        get = request
        request = None
        logger_htmx_attrs.debug("Legacy parameter style detected: first param treated as 'get' URL")
    
    attrs = []
    
    # Handle explicit HTTP method parameters with URL reversal
    if get:
        url_value = reverse(get) if ":" in str(get) else get
        attrs.append({"name": "hx-get", "value": url_value})
        logger_htmx_attrs.debug(f"GET mapped: {get} -> {url_value}")
        
    if post:
        url_value = reverse(post) if ":" in str(post) else post
        attrs.append({"name": "hx-post", "value": url_value})
        logger_htmx_attrs.debug(f"POST mapped: {post} -> {url_value}")
        
    if put:
        url_value = reverse(put) if ":" in str(put) else put
        attrs.append({"name": "hx-put", "value": url_value})
        logger_htmx_attrs.debug(f"PUT mapped: {put} -> {url_value}")
        
    if delete:
        url_value = reverse(delete) if ":" in str(delete) else delete
        attrs.append({"name": "hx-delete", "value": url_value})
        logger_htmx_attrs.debug(f"DELETE mapped: {delete} -> {url_value}")

    # Handle other explicit parameters
    if target:
        attrs.append({"name": "hx-target", "value": target})
    if swap:
        attrs.append({"name": "hx-swap", "value": swap})
    if trigger:
        attrs.append({"name": "hx-trigger", "value": trigger})
    if headers:
        # Handle both dict and string headers
        if isinstance(headers, dict):
            headers_value = json.dumps(headers)
        else:
            headers_value = headers
        attrs.append({"name": "hx-headers", "value": headers_value})
    if push_url is not None:
        attrs.append({"name": "hx-push-url", "value": str(push_url).lower()})
    if vals:
        attrs.append({"name": "hx-vals", "value": vals})
    if params:
        attrs.append({"name": "hx-params", "value": params})

    # Handle X-Tab special header
    if xtab:
        tab_name, func, command, version = xtab
        x_tab_value = f"{tab_name}:{version}:{func}:{command}"
        x_tab_header = f'{{"X-Tab":"{x_tab_value}"}}'
        attrs.append({"name": "hx-headers", "value": x_tab_header})
        logger_htmx_attrs.debug(f"X-Tab header added: {x_tab_value}")
    
    # Handle additional kwargs with snake_case -> hx-kebab-case conversion
    for key, value in kwargs.items():
        if key.startswith('on_'):
            # Handle event handlers like on_click -> hx-on:click
            event = key.replace('on_', '')
            attr_name = f'hx-on:{event}'
            attrs.append({'name': attr_name, 'value': value})
            logger_htmx_attrs.debug(f"Event handler mapped: {key} -> {attr_name}")
        else:
            # Handle standard attributes like loading_states -> hx-loading-states
            attr_name = f'hx-{key.replace("_", "-")}'
            attrs.append({'name': attr_name, 'value': value})
            logger_htmx_attrs.debug(f"Attribute mapped: {key} -> {attr_name}")
    
    logger_htmx_attrs.info(f"HTMX attributes built successfully: {len(attrs)} total attributes")
    logger_htmx_performance.debug(f"Attribute generation performance: {len(attrs)} attrs, URL_reversal={'yes' if any(':' in str(v) for v in [get,post,put,delete] if v) else 'no'}")
    
    return attrs



def htmx_form_submit(form_url, target_id='#form-container'):
    """Predefined HTMX config for form submissions"""
    logger_htmx_forms.debug(f"Creating form submit HTMX config: url={form_url}, target={target_id}")
    
    attrs = build_htmx_attrs(
        post=form_url,
        trigger='submit',
        target=target_id,
        swap='outerHTML',
        indicator='#form-loading',
        on_before_request="disableFormButtons()",
        on_after_request="enableFormButtons()"
    )
    
    logger_htmx_forms.info(f"Form submit HTMX config created: url={form_url}, target={target_id}")
    return attrs


def htmx_infinite_scroll(load_url, trigger_element='.load-more'):
    """Predefined HTMX config for infinite scroll"""
    logger_htmx_impl.debug(f"Creating infinite scroll HTMX config: url={load_url}, trigger={trigger_element}")
    
    attrs = build_htmx_attrs(
        get=load_url,
        trigger='intersect once',
        target='#content-list',
        swap='beforeend',
        indicator='#scroll-loading'
    )
    
    logger_htmx_impl.info(f"Infinite scroll HTMX config created: url={load_url}")
    logger_htmx_performance.debug(f"Infinite scroll performance: trigger_element={trigger_element}")
    return attrs


def validate_htmx_request(request):
    """Enhanced HTMX request validation"""
    logger_htmx_validation.debug("Starting HTMX request validation")
    
    # Check if request has HX-Request header
    if not request.headers.get('HX-Request'):
        logger_htmx_validation.warning("HTMX validation FAILED: Missing HX-Request header")
        logger_htmx_security.warning(f"Non-HTMX request to HTMX endpoint: IP={request.META.get('REMOTE_ADDR')}")
        return False
    
    # Check for expected HTMX target (allow common patterns)
    allowed_targets = ['.main-content', '#main-content', '#content', 'body', '.content', '#form-container']
    hx_target = request.headers.get('HX-Target')
    if hx_target and hx_target not in allowed_targets:
        logger_htmx_validation.warning(f"HTMX validation WARNING: Unusual target {hx_target} (allowed: {allowed_targets})")
        logger_htmx_security.warning(f"HTMX unusual target: target={hx_target}, IP={request.META.get('REMOTE_ADDR')}")
        # Don't fail - just log for monitoring
        # return False
    
    logger_htmx_validation.info("HTMX request validation SUCCESS")
    logger_htmx_security.debug(f"Valid HTMX request: target={hx_target or 'default'}")
    return True


def is_htmx_request(request):
    """
    Check if request is an HTMX request
    Returns: bool
    """
    logger_htmx_impl.debug("Checking if request is HTMX")
    
    is_htmx = getattr(request, "htmx", False) or request.headers.get("HX-Request") == "true"
    
    logger_htmx_impl.debug(f"HTMX request check result: {is_htmx}")
    return is_htmx



def render_htmx(request, template_name, context=None, status=200):
    """
    Renders a template for HTMX requests, falling back to normal render if not HTMX.
    """
    logger_htmx_impl.debug(f"HTMX render function called for template: {template_name}")
    
    context = context or {}
    is_htmx = getattr(request, "htmx", False) or request.headers.get("HX-Request") == "true"
    
    logger_htmx_impl.info(f"HTMX render: template={template_name}, is_htmx={is_htmx}, status={status}")
    logger_htmx_performance.debug(f"Template render performance tracking: {template_name}")
    
    if is_htmx:
        logger_htmx_impl.debug("Rendering for HTMX request")
    else:
        logger_htmx_impl.debug("Rendering for regular HTTP request")
    
    return render(request, template_name, context=context, status=status)


def hx_redirect(url: str) -> HttpResponse:
    """Create HTMX redirect response"""
    logger_htmx_impl.info(f"Creating HTMX redirect to: {url}")
    logger_htmx_security.debug(f"HTMX redirect security check: url={url}")
    
    resp = HttpResponse("")
    resp["HX-Redirect"] = url
    
    logger_htmx_impl.debug(f"HTMX redirect response created successfully for: {url}")
    return resp


def hx_refresh() -> HttpResponse:
    """Trigger a client-side page refresh"""
    logger_htmx_impl.info("Creating HTMX refresh response")
    resp = HttpResponse("")
    resp["HX-Refresh"] = "true"
    return resp


def hx_location(url: str, **kwargs) -> HttpResponse:
    """Navigate to a new location without a page refresh"""
    logger_htmx_impl.info(f"Creating HTMX location response: {url}")
    
    resp = HttpResponse("")
    location_data = {"path": url}
    location_data.update(kwargs)  # Allow target, swap, etc.
    resp["HX-Location"] = json.dumps(location_data)
    
    return resp


def hx_push_url(url: str) -> HttpResponse:
    """Push a new URL into the browser's history stack"""
    logger_htmx_impl.info(f"Creating HTMX push-url response: {url}")
    
    resp = HttpResponse("")
    resp["HX-Push-Url"] = url
    return resp


def hx_replace_url(url: str) -> HttpResponse:
    """Replace the current URL in the browser's history"""
    logger_htmx_impl.info(f"Creating HTMX replace-url response: {url}")
    
    resp = HttpResponse("")
    resp["HX-Replace-Url"] = url
    return resp


def hx_retarget(target: str) -> HttpResponse:
    """Change the target of the response"""
    logger_htmx_impl.info(f"Creating HTMX retarget response: {target}")
    
    resp = HttpResponse("")
    resp["HX-Retarget"] = target
    return resp


def hx_reswap(swap_method: str) -> HttpResponse:
    """Change the swap method of the response"""
    logger_htmx_impl.info(f"Creating HTMX reswap response: {swap_method}")
    
    resp = HttpResponse("")
    resp["HX-Reswap"] = swap_method
    return resp


def hx_trigger(event_name: str, payload=None, status=200):
    """Create HTMX trigger response"""
    logger_htmx_impl.debug(f"Creating HTMX trigger: event_name={event_name}, payload={payload}, status={status}")
    
    resp = HttpResponse(status=status)
    
    # Accept either a single event or a dict of events
    if isinstance(event_name, dict):
        logger_htmx_impl.debug(f"Processing multiple events: {list(event_name.keys())}")
        # Merge all events into HX-Trigger
        resp["HX-Trigger"] = json.dumps(event_name)
        logger_htmx_impl.info(f"HTMX trigger created with {len(event_name)} events")
    else:
        trigger_data = {event_name: payload} if payload is not None else event_name
        resp["HX-Trigger"] = json.dumps(trigger_data)
        logger_htmx_impl.info(f"HTMX trigger created: event={event_name}, has_payload={payload is not None}")
    
    logger_htmx_performance.debug(f"HTMX trigger performance: event_count={len(event_name) if isinstance(event_name, dict) else 1}")
    return resp



# HTMX-aware login_required that shows login form inline instead of redirecting
def htmx_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        logger_htmx_auth.debug(f"HTMX login decorator activated for view: {view_func.__name__}")
        
        if not request.user.is_authenticated:
            logger_htmx_auth.warning(f"Unauthenticated access attempt to protected view: {view_func.__name__}")
            logger_htmx_security.warning(f"Authentication required: view={view_func.__name__}, IP={request.META.get('REMOTE_ADDR')}")
            
            # Check if this is an HTMX request
            if request.headers.get('HX-Request') == 'true':
                logger_htmx_auth.info(f"Showing inline login form for HTMX request to view: {view_func.__name__}")
                # Instead of redirecting, return the login form HTML using HTMX defaults
                from core.forms.auth_forms import LoginForm
                from core.utils.context_processors import htmx_defaults
                
                # Get HTMX defaults for proper targeting and headers
                htmx_context = htmx_defaults(request)
                form = LoginForm(request=request, htmx_defaults=htmx_context.get('htmx_defaults', {}))
                
                context = {
                    'title': 'Login Required',
                    'form': form,
                    'page_title': 'Please Sign In',
                    'message': 'Please sign in to continue',
                    'login_submit_url': reverse('core:login_submit'),
                    'htmx_defaults': htmx_context.get('htmx_defaults', {}),
                }
                
                try:
                    from django.shortcuts import render
                    logger_htmx_auth.info("Rendering HTMX login form template")
                    return render(request, 'core/auth/login_form_crispy.html', context)
                except Exception as e:
                    logger_htmx_auth.error(f"Failed to render login form template: {str(e)}")
                    logger_htmx_auth.warning("Falling back to hardcoded HTML login form")
                    # Fallback HTML if template fails
                    html_content = f"""
                    <div class="container my-5">
                        <div class="row justify-content-center">
                            <div class="col-md-5">
                                <div class="card shadow-lg">
                                    <div class="card-header bg-warning text-dark text-center">
                                        <h4><i class="fas fa-lock me-2"></i>Login Required</h4>
                                    </div>
                                    <div class="card-body">
                                        <p class="text-center">Please sign in to access this content.</p>
                                        <div class="text-center">
                                            <a href="{reverse('core:login_access_view')}" 
                                               class="btn btn-primary"
                                               hx-get="{reverse('core:login_access_view')}" 
                                               hx-target="#main-content">
                                                <i class="fas fa-sign-in-alt me-2"></i>Sign In
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                    logger_htmx_auth.info("Returning fallback HTML login form")
                    return HttpResponse(html_content)
            else:
                logger_htmx_auth.info(f"Redirecting non-HTMX request to login page for view: {view_func.__name__}")
                # For non-HTMX requests, redirect to our login page
                try:
                    redirect_url = reverse('core:login_access_view')
                    logger_htmx_auth.debug(f"Login redirect URL resolved: {redirect_url}")
                    return redirect(redirect_url)
                except Exception as e:
                    logger_htmx_auth.error(f"Failed to reverse login URL: {str(e)}")
                    logger_htmx_auth.warning("Using fallback login URL")
                    # Fallback if reverse fails
                    return redirect('/login_access_view/')
        
        logger_htmx_auth.debug(f"User authenticated, proceeding to view: {view_func.__name__}")
        logger_htmx_security.debug(f"Authenticated access granted: user={request.user.username}, view={view_func.__name__}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view




def parse_xtab_header(request):
    """
    Parse X-Tab header into a structured dict
    
    Expected format: "tab:version:function:command"
    Example: "profile:1.0:load:view" -> {
        'tab': 'profile',
        'version': '1.0', 
        'function': 'load',
        'command': 'view',
        'raw': 'profile:1.0:load:view'
    }
    
    Returns:
        dict: Parsed X-Tab components or None if header missing
    """
    logger_htmx_impl.debug("Parsing X-Tab header from request")
    
    header = request.headers.get("X-Tab")
    if not header:
        logger_htmx_impl.debug("No X-Tab header found in request")
        return None

    logger_htmx_impl.debug(f"Found X-Tab header: {header}")
    
    parts = header.split(":")
    
    # Validate minimum required parts
    if len(parts) < 4:
        logger_htmx_validation.warning(f"Invalid X-Tab header format: {header} (expected 4 parts, got {len(parts)})")
        logger_htmx_security.warning(f"Malformed X-Tab header attempt: {header}, IP={request.META.get('REMOTE_ADDR')}")
        return None
    
    parsed_xtab = {
        "tab": parts[0] if parts[0] else None,
        "version": parts[1] if parts[1] else None,
        "function": parts[2] if parts[2] else None,
        "command": parts[3] if parts[3] else None,
        "raw": header,
        "parts_count": len(parts)
    }
    
    # Add any extra parts as additional data
    if len(parts) > 4:
        parsed_xtab["extra"] = parts[4:]
        logger_htmx_impl.debug(f"X-Tab header has {len(parts) - 4} extra parts: {parts[4:]}")
    
    logger_htmx_impl.info(f"X-Tab header parsed successfully: tab={parsed_xtab['tab']}, function={parsed_xtab['function']}, command={parsed_xtab['command']}")
    logger_htmx_performance.debug(f"X-Tab parsing: {len(parts)} parts processed")
    
    return parsed_xtab


def validate_xtab_request(request, expected_tab=None, expected_function=None):
    """
    Validate X-Tab header against expected values
    
    Args:
        request: Django request object
        expected_tab: Expected tab name (optional)
        expected_function: Expected function name (optional)
        
    Returns:
        tuple: (is_valid: bool, parsed_xtab: dict)
    """
    logger_htmx_validation.debug(f"Validating X-Tab request: expected_tab={expected_tab}, expected_function={expected_function}")
    
    parsed_xtab = parse_xtab_header(request)
    
    if not parsed_xtab:
        logger_htmx_validation.warning("X-Tab validation FAILED: No valid X-Tab header found")
        return False, None
    
    # Validate expected tab
    if expected_tab and parsed_xtab['tab'] != expected_tab:
        logger_htmx_validation.error(f"X-Tab validation FAILED: Expected tab '{expected_tab}', got '{parsed_xtab['tab']}'")
        logger_htmx_security.warning(f"X-Tab tab mismatch: expected={expected_tab}, actual={parsed_xtab['tab']}, IP={request.META.get('REMOTE_ADDR')}")
        return False, parsed_xtab
    
    # Validate expected function
    if expected_function and parsed_xtab['function'] != expected_function:
        logger_htmx_validation.error(f"X-Tab validation FAILED: Expected function '{expected_function}', got '{parsed_xtab['function']}'")
        logger_htmx_security.warning(f"X-Tab function mismatch: expected={expected_function}, actual={parsed_xtab['function']}, IP={request.META.get('REMOTE_ADDR')}")
        return False, parsed_xtab
    
    logger_htmx_validation.info(f"X-Tab validation SUCCESS: tab={parsed_xtab['tab']}, function={parsed_xtab['function']}")
    return True, parsed_xtab


def xtab_required(expected_tab=None, expected_function=None):
    """
    Decorator to require and validate X-Tab headers on views
    
    Usage:
        @xtab_required(expected_tab='profile', expected_function='load')
        def my_view(request):
            xtab = request.xtab  # Parsed X-Tab data available here
            return HttpResponse("Success")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            logger_htmx_auth.debug(f"X-Tab decorator activated for view: {view_func.__name__}")
            
            is_valid, parsed_xtab = validate_xtab_request(request, expected_tab, expected_function)
            
            if not is_valid:
                logger_htmx_auth.error(f"X-Tab validation failed for view: {view_func.__name__}")
                return HttpResponse("Invalid X-Tab header", status=400)
            
            # Add parsed X-Tab to request for use in view
            request.xtab = parsed_xtab
            
            logger_htmx_auth.debug(f"X-Tab validation successful, proceeding to view: {view_func.__name__}")
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator



# #######################
# Documentation
# # Complete HTMX Attributes Reference Guide

# ## Overview
# This document provides a comprehensive reference for all HTMX attributes available for use in HTMX applications. HTMX attributes control how hyperx-elements interact with servers, handle events, and manage content updates.

# ## Core HTTP Method Attributes

# ### Request Methods
# 
# hx-get="/url"           <!-- Send GET request -->
# hx-post="/url"          <!-- Send POST request -->
# hx-put="/url"           <!-- Send PUT request -->
# hx-patch="/url"         <!-- Send PATCH request -->
# hx-delete="/url"        <!-- Send DELETE request -->
# 

# ### Examples
# 
# <button hx-get="/api/users">Load Users</button>
# <form hx-post="/submit">Submit Form</form>
# <button hx-delete="/api/user/123">Delete User</button>
# 

# ## Content Targeting & Swapping

# ### Target Selection
# 
# hx-target="#element-id"     <!-- Target specific element by ID -->
# hx-target=".class-name"     <!-- Target by class -->
# hx-target="closest div"     <!-- Target closest parent div -->
# hx-target="find input"      <!-- Target child input -->
# hx-target="next"            <!-- Target next sibling -->
# hx-target="previous"        <!-- Target previous sibling -->
# hx-target="this"            <!-- Target the element itself -->
# 

# ### Content Swapping
# 
# hx-swap="innerHTML"         <!-- Replace inner content (default) -->
# hx-swap="outerHTML"         <!-- Replace entire element -->
# hx-swap="beforebegin"       <!-- Insert before element -->
# hx-swap="afterbegin"        <!-- Insert after opening tag -->
# hx-swap="beforeend"         <!-- Insert before closing tag -->
# hx-swap="afterend"          <!-- Insert after element -->
# hx-swap="delete"            <!-- Delete target element -->
# hx-swap="none"              <!-- Don't swap content -->
# 

# ### Swap Modifiers
# 
# hx-swap="innerHTML transition:true"     <!-- Enable transitions -->
# hx-swap="innerHTML swap:1s"             <!-- Delay swap by 1 second -->
# hx-swap="innerHTML settle:2s"           <!-- Settle duration 2 seconds -->
# hx-swap="innerHTML ignoreTitle:true"    <!-- Ignore title updates -->
# hx-swap="innerHTML scroll:top"          <!-- Scroll to top after swap -->
# hx-swap="innerHTML scroll:bottom"       <!-- Scroll to bottom after swap -->
# hx-swap="innerHTML show:top"            <!-- Show top of target -->
# hx-swap="innerHTML show:bottom"         <!-- Show bottom of target -->
# hx-swap="innerHTML focus-scroll:false"  <!-- Disable focus scrolling -->
# 

# ### Content Selection
# 
# hx-select="#content"        <!-- Select part of response -->
# hx-select-oob="#sidebar"    <!-- Out-of-band selection -->
# 

# ## Event Triggering

# ### Basic Triggers
# 
# hx-trigger="click"          <!-- On click -->
# hx-trigger="submit"         <!-- On form submit -->
# hx-trigger="change"         <!-- On input change -->
# hx-trigger="load"           <!-- On element load -->
# hx-trigger="revealed"       <!-- When scrolled into view -->
# hx-trigger="intersect"      <!-- When intersecting viewport -->
# 

# ### Trigger Modifiers
# 
# hx-trigger="click once"             <!-- Only trigger once -->
# hx-trigger="click changed"          <!-- Only if element changed -->
# hx-trigger="click delay:1s"         <!-- Delay 1 second -->
# hx-trigger="click throttle:1s"      <!-- Throttle to max once per second -->
# hx-trigger="keyup changed delay:500ms" <!-- Combined modifiers -->
# hx-trigger="click from:body"        <!-- Listen on body element -->
# hx-trigger="click target:.button"   <!-- Only from .button hyperx-elements -->
# hx-trigger="click consume"          <!-- Consume the event -->
# 

# ### Multiple Triggers
# 
# hx-trigger="click, keyup"           <!-- Multiple events -->
# hx-trigger="mouseenter once, click" <!-- Different modifiers -->
# 

# ### Polling
# 
# hx-trigger="every 2s"               <!-- Poll every 2 seconds -->
# hx-trigger="every 5m"               <!-- Poll every 5 minutes -->
# hx-trigger="load, every 30s"        <!-- Load then poll -->
# 

# ### Server-Sent Events
# 
# hx-trigger="sse:message"            <!-- SSE message event -->
# hx-trigger="sse:notification"       <!-- Custom SSE event -->
# 

# ## Form Data & Parameters

# ### Parameter Control
# 
# hx-params="*"               <!-- Include all form parameters -->
# hx-params="none"            <!-- Include no parameters -->
# hx-params="not csrf"        <!-- Exclude specific parameters -->
# hx-params="name,email"      <!-- Include only specific parameters -->
# 

# ### Additional Values
# 
# hx-vals='{"key":"value"}'           <!-- Static JSON values -->
# hx-vals="js:getFormData()"          <!-- Dynamic JavaScript values -->
# hx-vals='{"timestamp": "js:Date.now()"}' <!-- Mixed static/dynamic -->
# 

# ### Include Other Elements
# 
# hx-include="#other-form"            <!-- Include another form's data -->
# hx-include=".form-group"            <!-- Include hyperx-elements by class -->
# hx-include="[data-include]"         <!-- Include by attribute -->
# 

# ## Headers & Authentication

# ### Custom Headers
# 
# hx-headers='{"X-API-Key":"abc123"}'         <!-- Static headers -->
# hx-headers='{"Authorization":"Bearer xyz"}' <!-- Auth headers -->
# hx-headers="js:getHeaders()"                <!-- Dynamic headers -->
# 

# ### CSRF Protection
# 
# hx-headers='{"X-CSRFToken":"{{ csrf_token }}"}'  <!-- Django CSRF -->
# 

# ## User Interface & Feedback

# ### Loading Indicators
# 
# hx-indicator="#spinner"         <!-- Show specific spinner -->
# hx-indicator=".loading"         <!-- Show loading class -->
# hx-indicator="closest .card"    <!-- Show on closest card -->
# 

# ### Confirmation Dialogs
# 
# hx-confirm="Are you sure?"                  <!-- Simple confirmation -->
# hx-confirm="Delete this item permanently?"  <!-- Custom message -->
# 

# ### Element State Management
# 
# hx-disabled-elt="this"          <!-- Disable this element during request -->
# hx-disabled-elt="#submit-btn"   <!-- Disable specific element -->
# hx-disabled-elt="find button"   <!-- Disable child buttons -->
# 

# ## URL & History Management

# ### Browser History
# 
# hx-push-url="true"              <!-- Push new URL to history -->
# hx-push-url="/new-path"         <!-- Push specific URL -->
# hx-replace-url="true"           <!-- Replace current URL -->
# hx-replace-url="/updated-path"  <!-- Replace with specific URL -->
# 

# ### Progressive Enhancement
# 
# hx-boost="true"                 <!-- Boost all links/forms in element -->
# 

# ## Advanced Features

# ### Element Preservation
# 
# hx-preserve="true"              <!-- Preserve element during swaps -->
# 

# ### Inheritance Control
# 
# hx-disinherit="*"               <!-- Don't inherit any attributes -->
# hx-disinherit="hx-target"       <!-- Don't inherit specific attribute -->
# 

# ### Request Configuration
# 
# hx-encoding="multipart/form-data"   <!-- For file uploads -->
# hx-ext="json-enc"                   <!-- Use JSON encoding extension -->
# hx-sync="this:drop"                 <!-- Sync behavior -->
# hx-sync="closest form:abort"        <!-- Abort on form sync -->
# 

# ### Validation
# 
# hx-validate="true"              <!-- Enable client-side validation -->
# 

# ## Real-time Features

# ### WebSocket
# 
# hx-ws="connect:/ws/chat"        <!-- Connect to WebSocket -->
# hx-ws="send"                    <!-- Send via WebSocket -->
# 

# ### Server-Sent Events
# 
# hx-sse="connect:/events"        <!-- Connect to SSE endpoint -->
# hx-sse="swap:message"           <!-- Swap on SSE message -->
# 

# ## Event Handling (hx-on)

# ### Lifecycle Events
# 
# hx-on::before-request="showSpinner()"
# hx-on::after-request="hideSpinner()"
# hx-on::before-swap="prepareSwap()"
# hx-on::after-swap="initComponents()"
# hx-on::after-settle="focusFirst()"
# 

# ### Error Handling
# 
# hx-on::htmx:responseError="handleError(event)"
# hx-on::htmx:sendError="handleNetworkError(event)"
# hx-on::htmx:timeout="handleTimeout(event)"
# 

# ### Standard DOM Events
# 
# hx-on::click="trackClick()"
# hx-on::change="validateInput()"
# hx-on::focus="highlightField()"
# hx-on::blur="validateField()"
# 

# ## Extensions

# ### Core Extensions
# 
# hx-ext="json-enc"               <!-- JSON encoding -->
# hx-ext="morphdom-swap"          <!-- Morphdom swapping -->
# hx-ext="client-side-templates"  <!-- Client-side templating -->
# hx-ext="debug"                  <!-- Debug extension -->
# hx-ext="loading-states"         <!-- Auto loading states -->
# hx-ext="path-deps"              <!-- Path dependencies -->
# hx-ext="preload"                <!-- Preload extension -->
# hx-ext="response-targets"       <!-- Response-based targeting -->
# 

# ## Practical Examples

# ### Complete Form Example
# 
# <form hx-post="/submit"
#       hx-target="#result"
#       hx-swap="innerHTML"
#       hx-trigger="submit"
#       hx-confirm="Submit this form?"
#       hx-indicator="#spinner"
#       hx-disabled-elt="find button"
#       hx-headers='{"X-Requested-With":"XMLHttpRequest"}'
#       hx-on::before-request="validateForm()"
#       hx-on::after-request="resetForm()"
#       hx-on::htmx:responseError="showError(event)">
    
#     <input name="email" required>
#     <button type="submit">Submit</button>
# </form>
# 

# ### AJAX Button with Feedback
# 
# <button hx-delete="/api/item/123"
#         hx-target="closest .item"
#         hx-swap="outerHTML"
#         hx-confirm="Delete this item?"
#         hx-indicator=".spinner"
#         hx-disabled-elt="this"
#         hx-push-url="true"
#         hx-on::before-request="this.textContent = 'Deleting...'"
#         hx-on::after-request="showNotification('Deleted!')"
#         hx-on::htmx:responseError="this.textContent = 'Error'">
#     Delete Item
# </button>
# 

# ### Live Search
# 
# <input type="search" 
#        hx-get="/search"
#        hx-target="#results"
#        hx-trigger="keyup changed delay:500ms"
#        hx-indicator="#search-spinner"
#        hx-vals='{"type":"user"}'
#        hx-on::before-request="showSearching()"
#        hx-on::after-settle="highlightResults()"
#        placeholder="Search users...">
# 

# ### Infinite Scroll
# 
# <div hx-get="/api/items?page=2"
#      hx-target="#items"
#      hx-swap="afterend"
#      hx-trigger="revealed"
#      hx-indicator="#loading"
#      hx-on::after-request="updatePageCount()">
#     Loading more...
# </div>
# 

# ### File Upload
# 
# <form hx-post="/upload"
#       hx-encoding="multipart/form-data"
#       hx-target="#upload-result"
#       hx-indicator="#upload-progress"
#       hx-on::htmx:xhr:progress="updateProgress(event)"
#       hx-on::before-request="resetProgress()"
#       hx-on::after-request="completeUpload()">
    
#     <input type="file" name="file" required>
#     <button type="submit">Upload</button>
# </form>
# 

# ### Real-time Chat
# 
# <div hx-ext="ws" 
#      hx-ws="connect:/ws/chat/room1">
    
#     <div id="messages" 
#          hx-ws="swap:message"
#          hx-target="#messages"
#          hx-swap="beforeend">
#     </div>
    
#     <form hx-ws="send">
#         <input name="message" autocomplete="off">
#         <button type="submit">Send</button>
#     </form>
# </div>
# 

# ### Progressive Enhancement
# 
# <div hx-boost="true">
#     <!-- All links and forms automatically use HTMX -->
#     <a href="/page1">Page 1</a>
#     <a href="/page2">Page 2</a>
    
#     <form action="/search" method="get">
#         <input name="q" placeholder="Search...">
#         <button type="submit">Search</button>
#     </form>
# </div>
# 

# ### Polling with Error Handling
# 
# <div hx-get="/api/status"
#      hx-trigger="load, every 30s"
#      hx-target="#status"
#      hx-swap="innerHTML"
#      hx-on::before-request="showChecking()"
#      hx-on::after-request="showConnected()"
#      hx-on::htmx:responseError="showDisconnected()"
#      hx-on::htmx:sendError="showOffline()">
    
#     <div id="status">Checking status...</div>
# </div>
# 

# ## Attribute Combinations

# ### Common Patterns
# 
# <!-- Load and refresh pattern -->
# hx-get="/data" hx-trigger="load, every 5s" hx-target="#content"

# <!-- Form with validation -->
# hx-post="/submit" hx-validate="true" hx-disabled-elt="find button"

# <!-- Delete with confirmation -->
# hx-delete="/item/123" hx-confirm="Delete?" hx-target="closest .item" hx-swap="outerHTML"

# <!-- Search as you type -->
# hx-get="/search" hx-trigger="keyup changed delay:300ms" hx-target="#results"
# 

# ## Security Considerations

# ### CSRF Protection
# 
# <!-- Django CSRF -->
# hx-headers='{"X-CSRFToken":"{{ csrf_token }}"}'

# <!-- Laravel CSRF -->
# hx-headers='{"X-CSRF-TOKEN":"{{ csrf_token() }}"}'
# 

# ### Content Security Policy
# 
# <!-- Use nonce for inline handlers -->
# hx-on::click="handleClick()" nonce="{{nonce}}"
# 

# ## Performance Tips

# 1. **Use specific targets** instead of large DOM areas
# 2. **Implement proper caching** headers on server responses
# 3. **Use `hx-sync`** to prevent race conditions
# 4. **Debounce user input** with `delay:` modifier
# 5. **Use `hx-select`** to transfer only needed HTML
# 6. **Implement proper error handling** for better UX
# 7. **Use `hx-preserve`** for expensive-to-recreate hyperx-elements

# ## Debugging Attributes

# ### Debug Information
# 
# hx-ext="debug"                  <!-- Enable debug extension -->
# hx-on::htmx:beforeRequest="console.log('Request:', event)"
# hx-on::htmx:afterRequest="console.log('Response:', event)"
# 

# ### Common Debug Pattern
# 
# <div hx-get="/api/test"
#      hx-on::htmx:beforeRequest="console.log('Starting request')"
#      hx-on::htmx:afterRequest="console.log('Request completed', event.detail)"
#      hx-on::htmx:responseError="console.error('Request failed', event.detail)"
#      hx-on::htmx:sendError="console.error('Network error', event.detail)">
# </div>
# 

# ## Browser Compatibility

# HTMX works with:
# - Chrome/Edge 63+
# - Firefox 63+
# - Safari 12+
# - Internet Explorer 11 (with polyfills)

# ## Related Technologies

# HTMX works well with:
# - **Hyperscript** - For client-side scripting
# - **Alpine.js** - For reactive components  
# - **_hyperscript** - HTMX's companion scripting language
# - **Tailwind CSS** - For styling
# - **Bootstrap** - For UI components

# ---

##### EXAMPLE USAGE #####

# HTMX Event Reference Guide

# ## Overview
# This document provides a comprehensive reference for all HTMX event attributes that can be used with `hx-on:` for event handling in HTMX applications.

# ## Basic Syntax
# 
# hx-on::[event-name]="JavaScript code"
# 

# ## HTMX Lifecycle Events

# ### Full Event Names
# 
# hx-on::htmx:beforeRequest="..."     <!-- Before request is sent -->
# hx-on::htmx:afterRequest="..."      <!-- After response received -->
# hx-on::htmx:beforeSwap="..."        <!-- Before DOM swap -->
# hx-on::htmx:afterSwap="..."         <!-- After DOM swap -->
# hx-on::htmx:afterSettle="..."       <!-- After settle animations -->
# hx-on::htmx:beforeCleanup="..."     <!-- Before cleanup -->
# 

# ### Shortened Event Names
# 
# hx-on::before-request="..."         <!-- Same as htmx:beforeRequest -->
# hx-on::after-request="..."          <!-- Same as htmx:afterRequest -->
# hx-on::before-swap="..."            <!-- Same as htmx:beforeSwap -->
# hx-on::after-swap="..."             <!-- Same as htmx:afterSwap -->
# hx-on::after-settle="..."           <!-- Same as htmx:afterSettle -->
# 

# ### Event Execution Order
# 1. `before-request` - Fires before the request is sent
# 2. `after-request` - Fires when response is received
# 3. `before-swap` - Fires before DOM changes
# 4. `after-swap` - Fires immediately after DOM changes
# 5. `after-settle` - Fires after settle animations complete

# ## Error Handling Events

# 
# hx-on::htmx:responseError="..."     <!-- HTTP error response (4xx, 5xx) -->
# hx-on::htmx:sendError="..."        <!-- Network/send error -->
# hx-on::htmx:timeout="..."          <!-- Request timeout -->
# hx-on::htmx:validation:validate="..." <!-- Form validation event -->
# hx-on::htmx:validation:failed="..." <!-- Validation failed -->
# hx-on::htmx:validation:halted="..." <!-- Validation halted -->
# 

# ## Progress Events

# 
# hx-on::htmx:xhr:progress="..."      <!-- Upload/download progress -->
# hx-on::htmx:xhr:loadstart="..."     <!-- XMLHttpRequest load start -->
# hx-on::htmx:xhr:loadend="..."       <!-- XMLHttpRequest load end -->
# 

# ## History Management Events

# 
# hx-on::htmx:pushedIntoHistory="..." <!-- URL pushed to browser history -->
# hx-on::htmx:replacedInHistory="..." <!-- URL replaced in browser history -->
# hx-on::htmx:historyRestore="..."    <!-- History restored (back/forward) -->
# 

# ## WebSocket Events
# *Available when using `hx-ws` attribute*

# 
# hx-on::htmx:wsConnecting="..."      <!-- WebSocket connecting -->
# hx-on::htmx:wsOpen="..."            <!-- WebSocket connection opened -->
# hx-on::htmx:wsClose="..."           <!-- WebSocket connection closed -->
# hx-on::htmx:wsError="..."           <!-- WebSocket error -->
# hx-on::htmx:wsBeforeMessage="..."   <!-- Before WebSocket message processed -->
# hx-on::htmx:wsAfterMessage="..."    <!-- After WebSocket message processed -->
# 

# ## Server-Sent Events (SSE)
# *Available when using `hx-sse` attribute*

# 
# hx-on::htmx:sseConnecting="..."     <!-- SSE connecting -->
# hx-on::htmx:sseOpen="..."           <!-- SSE connection opened -->
# hx-on::htmx:sseClose="..."          <!-- SSE connection closed -->
# hx-on::htmx:sseError="..."          <!-- SSE error -->
# hx-on::htmx:sseBeforeMessage="..."  <!-- Before SSE message processed -->
# 

# ## Standard DOM Events

# ### Mouse Events
# 
# hx-on::click="..."                  <!-- Mouse click -->
# hx-on::dblclick="..."               <!-- Double click -->
# hx-on::mousedown="..."              <!-- Mouse button down -->
# hx-on::mouseup="..."                <!-- Mouse button up -->
# hx-on::mouseenter="..."             <!-- Mouse enter element -->
# hx-on::mouseleave="..."             <!-- Mouse leave element -->
# hx-on::mouseover="..."              <!-- Mouse over element -->
# hx-on::mouseout="..."               <!-- Mouse out of element -->
# hx-on::mousemove="..."              <!-- Mouse move -->
# 

# ### Keyboard Events
# 
# hx-on::keydown="..."                <!-- Key pressed down -->
# hx-on::keyup="..."                  <!-- Key released -->
# hx-on::keypress="..."               <!-- Key pressed (deprecated) -->
# 

# ### Form Events
# 
# hx-on::submit="..."                 <!-- Form submission -->
# hx-on::change="..."                 <!-- Input value changed -->
# hx-on::input="..."                  <!-- Input value changing -->
# hx-on::focus="..."                  <!-- Element gained focus -->
# hx-on::blur="..."                   <!-- Element lost focus -->
# hx-on::focusin="..."                <!-- Element or child gained focus -->
# hx-on::focusout="..."               <!-- Element or child lost focus -->
# hx-on::reset="..."                  <!-- Form reset -->
# hx-on::select="..."                 <!-- Text selected -->
# 

# ### Document/Window Events
# 
# hx-on::load="..."                   <!-- Element/document loaded -->
# hx-on::unload="..."                 <!-- Page unloading -->
# hx-on::beforeunload="..."           <!-- Before page unload -->
# hx-on::resize="..."                 <!-- Window resized -->
# hx-on::scroll="..."                 <!-- Scroll event -->
# hx-on::hashchange="..."             <!-- URL hash changed -->
# 

# ### Touch Events (Mobile)
# 
# hx-on::touchstart="..."             <!-- Touch started -->
# hx-on::touchend="..."               <!-- Touch ended -->
# hx-on::touchmove="..."              <!-- Touch moved -->
# hx-on::touchcancel="..."            <!-- Touch cancelled -->
# 

# ## Multiple Event Handlers

# You can use multiple `hx-on` attributes on the same element:

# 
# <div hx-get="/api/data"
#      hx-target="#content"
#      hx-trigger="click"
#      hx-on::before-request="showSpinner()"
#      hx-on::after-request="hideSpinner()"
#      hx-on::htmx:responseError="handleError(event)"
#      hx-on::click="trackClick()"
#      hx-on::mouseenter="showTooltip()"
#      hx-on::mouseleave="hideTooltip()">
#     Load Data
# </div>
# 

# ## Event Object Access

# Most events provide an event object with useful information:

# 
# hx-on::htmx:responseError="handleError(event)"
# hx-on::click="handleClick(event)"
# hx-on::keydown="handleKeyPress(event)"
# 

# ### Common Event Properties
# - `event.target` - The element that triggered the event
# - `event.detail` - HTMX-specific event details
# - `event.preventDefault()` - Prevent default behavior
# - `event.stopPropagation()` - Stop event bubbling

# ## Processing Order

# ### Event Registration
# - All `hx-on` attributes are registered in HTML order
# - Multiple handlers for the same event execute in registration order

# ### Event Execution
# - HTMX lifecycle events follow their natural sequence
# - Same event type handlers fire in HTML order
# - Different event types fire when their conditions are met

# ## Practical Examples

# ### Authentication Flow
# 
# <div hx-get="{% url 'acct:destroy' %}" 
#      hx-trigger="load"
#      hx-target="body" 
#      hx-swap="outerHTML"
#      hx-on::before-request="console.log('Checking auth status...')"
#      hx-on::after-settle="if(document.querySelector('.authenticated')) { window.location.href = '/dashboard/' }"
#      hx-on::htmx:responseError="console.error('Auth check failed:', event.detail)">
# </div>
# 

# ### Form with Validation
# 
# <form hx-post="/submit"
#       hx-target="#results"
#       hx-on::submit="validateForm(event)"
#       hx-on::htmx:validation:failed="highlightErrors(event)"
#       hx-on::before-request="disableForm()"
#       hx-on::after-request="enableForm()"
#       hx-on::htmx:responseError="showErrorMessage(event)">
#     <!-- form fields -->
# </form>
# 

# ### Interactive Button
# 
# <button hx-post="/action"
#         hx-on::click="trackButtonClick()"
#         hx-on::mouseenter="showPreview()"
#         hx-on::mouseleave="hidePreview()"
#         hx-on::before-request="this.disabled = true"
#         hx-on::after-request="this.disabled = false">
#     Action Button
# </button>
# 

# ### Loading States
# 
# <div hx-get="/data"
#      hx-trigger="load"
#      hx-on::before-request="document.getElementById('spinner').style.display = 'block'"
#      hx-on::after-settle="document.getElementById('spinner').style.display = 'none'"
#      hx-on::htmx:responseError="showErrorState()">
# </div>
# 

# ## Best Practices

# 1. **Use shortened event names** for cleaner HTML (`after-settle` vs `htmx:afterSettle`)
# 2. **Handle errors** with `htmx:responseError` and `htmx:sendError`
# 3. **Provide user feedback** during long operations using `before-request` and `after-request`
# 4. **Clean up resources** in appropriate lifecycle events
# 5. **Use event.preventDefault()** when needed to control default behaviors
# 6. **Keep JavaScript code simple** in attributes, use functions for complex logic
# 7. **Test event order** when using multiple handlers for the same event

# ## Related HTMX Attributes

# These attributes work together with `hx-on`:

# - `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete` - HTTP methods
# - `hx-target` - Where to put response
# - `hx-swap` - How to swap content
# - `hx-trigger` - What triggers the request
# - `hx-indicator` - Loading indicator
# - `hx-confirm` - Confirmation dialog
# - `hx-headers` - Custom headers
# - `hx-vals` - Additional form values

# ## Debugging Events

# Use browser developer tools to debug HTMX events:

# 
# <!-- Log all HTMX events for debugging -->
# <div hx-on::htmx:beforeRequest="console.log('beforeRequest:', event)"
#      hx-on::htmx:afterRequest="console.log('afterRequest:', event)"
#      hx-on::htmx:responseError="console.error('responseError:', event)">
# </div>
# 

# ---
