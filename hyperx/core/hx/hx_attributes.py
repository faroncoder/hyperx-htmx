

from django.shortcuts import render, redirect
from django.contrib import messages
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.urls import reverse
from functools import wraps
#from django.shortcuts import render
from django.template.loader import render_to_string

import json
import logging

# Comprehensive logging setup for HTMX implementation
logger_htmx_impl = logging.getLogger('hyperx.templatetags.htmx_implementation.main')
logger_htmx_attrs = logging.getLogger('hyperx.templatetags.htmx_implementation.attrs')
logger_htmx_forms = logging.getLogger('hyperx.templatetags.htmx_implementation.forms')
logger_htmx_validation = logging.getLogger('hyperx.templatetags.htmx_implementation.validation')
logger_htmx_auth = logging.getLogger('hyperx.templatetags.htmx_implementation.auth')
logger_htmx_security = logging.getLogger('hyperx.templatetags.htmx_implementation.security')
logger_htmx_performance = logging.getLogger('hyperx.templatetags.htmx_implementation.performance')




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




def htmx_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get("HX-Request") == "true":
                # Try primary template
                try:
                    return render(
                        request,
                        "core/auth/login_form_crispy.html",
                        {
                            "title": "Login Required",
                            "login_url": reverse("core:login_access_view"),
                        },
                    )
                except Exception:
                    # Render fallback template instead of inline HTML
                    html = render_to_string(
                        "core/htmx/login_fallback.html",
                        {"login_url": reverse("core:login_access_view")},
                    )
                    return HttpResponse(html)
            # Normal request: redirect
            return redirect("core:login_access_view")
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

