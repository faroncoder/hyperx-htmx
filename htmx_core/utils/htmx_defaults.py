import time
from django.shortcuts import render, resolve_url
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpRequest
from htmx_core.middleware.htmx_security import HTMXTokenManager
from functools import wraps
from django.urls import reverse


def htmx_defaults(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    one_time_token = HTMXTokenManager.generate_token(request, "general")
    return {
        "htmx_defaults": {
            "href": None,
            "hx-target": divplaceholder,
            "hx-trigger": "click",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-indicator": "#global-loader",
            "hx-timeout": "5000",
            "hx-boost": "true",
            "hx-redirect": None,
            "hx-history": "false",
            "hx-on::click": "this.classList.add('active')",
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-General-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{one_time_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }

def htmx_upload_defaults(request):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    upload_token = HTMXTokenManager.generate_token(request, "upload", expires_in=1800)
    return {
        "htmx_upload_defaults": {
            "href": None,
            "hx-target": ".main-content",
            "hx-trigger": "change",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-indicator": "#global-loader",
            "hx-boost": "true",
            "hx-redirect": None,
            "hx-timeout": "30000",
            "hx-encoding": "multipart/form-data",
            "hx-disabled-elt": "this",
            "hx-history": "false",
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Upload-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{upload_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }

def htmx_form_defaults(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    form_token = HTMXTokenManager.generate_token(request, "form", expires_in=900)
    return {
        "htmx_form_defaults": {
            "href": None,
            "hx-target": divplaceholder,
            "hx-trigger": "submit",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-indicator": "#global-loader",
            "hx-boost": "true",
            "hx-redirect": None,
            "hx-timeout": "15000",
            "hx-disabled-elt": "find button[type='submit']",
            "hx-on::after-request": "this.reset()",
            "hx-history": "false",
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Form-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{form_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }

def htmx_search_defaults(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    search_token = HTMXTokenManager.generate_token(request, "search", expires_in=300)
    return {
        "htmx_search_defaults": {
            "href": "",
            "hx-target": divplaceholder,
            "hx-trigger": "keyup changed delay:300ms, search",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-indicator": "#global-loader",
            "hx-timeout": "10000",
            "hx-redirect": None,
            "hx-select": ".main-content",
            "hx-boost": "true",
            "hx-history": "false",
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Search-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{search_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }

def htmx_sidemenu_defaults(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    menu_token = HTMXTokenManager.generate_token(request, "sidemenu", expires_in=600)
    return {
        "htmx_sidemenu_defaults": {
            "href": "",
            "hx-target": divplaceholder,
            "hx-trigger": "click",
            "hx-push-url": "false",
            "hx-swap": "innerHTML show:window:top",
            "hx-indicator": "#global-loader",
            "hx-timeout": "8000",
            "hx-redirect": None,
            "hx-boost": "true",
            "hx-swap-oob": "true",
            "hx-select": ".main-content",
            "hx-history": "false",
            "hx-on::before-request": (
                "this.setAttribute('aria-pressed', 'true'); "
                "this.setAttribute('aria-expanded', 'true')"
            ),
            "hx-on::after-request": (
                "this.setAttribute('aria-pressed', 'false'); "
                "this.setAttribute('aria-expanded', 'false'); "
                "this.setAttribute('aria-current', 'page')"
            ),
            "hx-on::click": (
                "document.querySelectorAll('.sidemenu-item').forEach(item => item.classList.remove('active')); "
                "this.classList.add('active')"
            ),
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Menu-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{menu_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }


def htmx_dashboard(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    dash_token = HTMXTokenManager.generate_token(request, "dashboard", expires_in=600)
    return {
        "htmx_dashboard_panel": {
            "href": "",
            "hx-target": divplaceholder,
            "hx-trigger": "click",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-indicator": "#global-loader",
            "hx-timeout": "8000",
            "hx-redirect": None,
            "hx-boost": "true",
            # "hx-swap-oob": "true",
            # "hx-select": ".main-content",
            "hx-history": "false",
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Dashboard-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{dash_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }


def htmx_xtab_defaults(request, divplaceholder):
    """
    HTMX defaults specifically configured for X-Tab tabbed interfaces.
    
    Optimized for:
    - Fast tab switching with minimal latency
    - X-Tab header detection for server-side tab routing
    - Smooth UX with proper indicators and timeouts
    - Tab-specific token security
    """
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    xtab_token = HTMXTokenManager.generate_token(request, "xtab", expires_in=1200)  # 20 minutes for tab sessions
    
    return {
        "htmx_xtab_defaults": {
            "href": "",
            "hx-target": divplaceholder,
            "hx-trigger": "click",
            "hx-push-url": "false",  # X-Tabs should not change URL
            "hx-swap": "innerHTML show:window:top",
            "hx-indicator": ".x-tab-loading",  # X-Tab specific loading indicator
            "hx-timeout": "6000",  # Slightly longer for complex tab content
            "hx-redirect": None,
            "hx-boost": "true",
            "hx-history": "false",  # Tabs don't affect browser history
            "hx-select": None,  # Let server determine content selection
            "hx-on::before-request": (
                "this.setAttribute('aria-selected', 'true'); "
                "document.querySelectorAll('[data-x-tab]').forEach(tab => { "
                "if (tab !== this) tab.setAttribute('aria-selected', 'false'); "
                "tab.classList.remove('active'); "
                "}); "
                "this.classList.add('active')"
            ),
            "hx-on::after-request": (
                "this.setAttribute('aria-busy', 'false'); "
                "if (window.HTMXUtils && window.HTMXUtils.reinitializeScripts) { "
                "window.HTMXUtils.reinitializeScripts(event.detail.target); "
                "}"
            ),
            "hx-on::after-request-error": (
                "this.setAttribute('aria-selected', 'false'); "
                "this.classList.remove('active'); "
                "console.error('X-Tab loading failed:', event.detail)"
            ),
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Tab-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{xtab_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }


def htmx_modal_defaults(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"
    modal_token = HTMXTokenManager.generate_token(request, "modal", expires_in=600)
    return {
        "htmx_modal_defaults": {
            "href": "javascript:void(0)",
            "hx-target": divplaceholder,
            "hx-trigger": "click",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-indicator": "#global-loader",
            "hx-boost": "true",
            "hx-timeout": "8000",
            "hx-history": "false",
            "data-bs-toggle": "modal",
            "data-bs-target": "#modal",
            "hx-on::before-request": "this.setAttribute('aria-busy', 'true')",
            "hx-on::after-request": (
                "if(event.detail.target.matches('.modal-content')) { "
                "var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('modal')); modal.show(); }"
            ),
            "hx-on::after-request-complete": "this.setAttribute('aria-busy', 'false')",
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Modal-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{modal_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }

def htmx_clean_url_defaults(request, divplaceholder):
    session_key = request.session.session_key or "no-session"
    siteuser = request.META.get("HTTP_X_SITE_USER") or "anonymous"
    sessionidentifier = request.META.get("HTTP_X_SESSION_ID") or "no-session"    
    clean_token = HTMXTokenManager.generate_token(request, "clean", expires_in=600)
    return {
        "htmx_clean_defaults": {
            "href": None,
            "hx-target": divplaceholder,
            "hx-trigger": "click",
            "hx-push-url": "false",
            "hx-swap": "innerHTML",
            "hx-boost": "true",
            "hx-indicator": "#global-loader",
            "hx-redirect": None,
            "hx-timeout": "5000",
            "hx-history": "false",
            "hx-on::before-request": (
                "window.history.replaceState(null, '', window.location.origin)"
            ),
            "hx-on::after-request": (
                "window.history.replaceState(null, '', window.location.origin)"
            ),
            "hx-headers": (
                f'{{"X-CSRFToken": "{{{{ csrf_token }}}}", '
                f'"X-Session-ID": "{session_key}", '
                f'"X-Requested-With": "XMLHttpRequest", '
                f'"X-Clean-Request": "true", '
                f'"X-Site-User": "{siteuser}", '
                f'"X-Session-Identifier": "{sessionidentifier}", '
                f'"X-One-Time-Token": "{clean_token}", '
                f'"X-Route-Request": "true"}}'
            ),
        }
    }

def debug_to_browser(request):
    if getattr(settings, "DEBUG", False):
        debug_info = globals().get("get_debug_info", lambda: None)() if "get_debug_info" in globals() else None
        if debug_info:
            return {"debug_info": debug_info}
    return {}

def htmx_salt_context(request):
    salt, components = HTMXTokenManager.generate_dom_salt(request)
    sample_token = HTMXTokenManager.generate_token(request, "hashsalt", expires_in=600)
    sample_retoken, retoken_components = HTMXTokenManager.generate_client_retoken(
        request, sample_token, "hashsalt"
    )
    return {
        "salt_context": {
            "salt": salt,
            "components": components,
            "session_key": request.session.session_key or "no-session",
            "sample_token": sample_token,
            "sample_retoken": sample_retoken,
            "timestamp_interval": int(time.time()) // 300,
            "client_hints": {
                "session_key_hint": (request.session.session_key or "no-session")[:8],
                "dom_fingerprint": f"body-{len(request.path)}-{request.method}",
                "csrf_available": bool(request.META.get("CSRF_COOKIE")),
            },
        }
    }

def htmx_redirect(url, force_clear=True):
    """
    Create an HTMX-compatible redirect response.
    Disables HX-Redirect and relies on middleware to convert to HX-Render.
    """
    response = HttpResponseRedirect(url)
    
    # Prevent client-side HX-Redirect; middleware will handle rendering
    response['HX-Redirect'] = 'false'
    
    # Mark for force clearing if requested (middleware can check this)
    if force_clear:
        response._htmx_force_clear = True
    
    return response


def smart_redirect(request, url, force_clear=False):
    # automatically disable redirect and turn the callback as a rendering at every cost

    from django.urls import resolve
    try:
        # Remove query string for URL resolution
        path_only = url.split('?')[0]
        resolved = resolve(path_only)
        view_func = resolved.func

        # Prepare a new request object with updated path and query string
        from django.http import QueryDict
        new_request = request.__class__(request.environ.copy())
        new_request.user = request.user
        new_request.session = request.session
        new_request.META = request.META.copy()
        new_request.method = request.method
        new_request.content_type = request.content_type

        if '?' in url:
            path, query_string = url.split('?', 1)
            new_request.path = path
            new_request.path_info = path
            new_request.META['QUERY_STRING'] = query_string
            new_request.GET = QueryDict(query_string)
        else:
            new_request.path = url
            new_request.path_info = url
            new_request.GET = QueryDict()

        new_request.POST = request.POST.copy()
        new_request.FILES = request.FILES.copy()

        # Call the target view function directly
        response = view_func(
            new_request,
            *resolved.args,
            **resolved.kwargs
        )
        return response
    except Exception as e:
        # Fallback: show error message
        error_html = f'''
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            Could not render target view for URL "{url}": {e}
        </div>
        '''
        return HttpResponse(error_html, status=500)


def no_redirect_for_htmx(view_func):
    """
    Decorator that prevents redirects in HTMX views
    kill redirect responses and instead returns an error message
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        if (request.headers.get('HX-Request') == 'true' and 
            isinstance(response, HttpResponseRedirect)):
            
            # Log the attempted redirect
            print(f"HTMX: Blocked redirect to {response.url}")
            
            # Return error instead
            error_html = f'''
            <div class="alert alert-warning" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Debug: Redirect to {response.url} was blocked for HTMX compatibility.
            </div>
            '''
            return HttpResponse(error_html)
        
        return response
    
    return wrapper


def get_redirect_url_name(url):
    """
    Get the URL name from a redirect URL for logging purposes
    """
    try:
        resolved = resolve(url.split('?')[0])
        return f"{resolved.namespace}:{resolved.url_name}" if resolved.namespace else resolved.url_name
    except:
        return url
    
    
def partial_render(request, template_name, context=None):
    """
    Render a partial template for HTMX
    Always renders the template without layout
    """
    if context is None:
        context = {}
    
    # Add HTMX context
    context.update({
        'is_htmx': True,
        'is_partial': True,
    })
    
    return render(request, template_name, context)


def htmx_tabber():
    """
    DEPRECATED: Legacy function replaced by X-Tab system.
    
    Use htmx_core.utils.htmx_x_tab_registry.export_x_tab_manifest_json() instead.
    This provides the same functionality with enhanced features.
    """
    # Import the enhanced X-Tab system replacement
    try:
        from htmx_core.utils.htmx_x_tab_registry import TabRegistry
        registry = TabRegistry()
        manifest = registry.generate_tab_manifest()
        
        # Return simplified format for backward compatibility
        listing = []
        for app_name, app_data in manifest['apps'].items():
            for tab in app_data['tabs']:
                listing.append({
                    "url_pattern": tab['tab_id'],
                    "tab_name": tab['name'],
                    "tab_slug": tab['tab_slug']
                })
        return listing
    except ImportError:
        # Fallback to original implementation if X-Tab system not available
        from django.utils.text import slugify
        from django.conf import settings
        from pathlib import Path
        import json, os
        from htmx_core.utils.htmx_x_tab_registry import TabRegistry

        registry = TabRegistry()
        mapping = registry.generate_tab_manifest()

        # build list with slug
        listing = [
            {
                "url_pattern": url_name,
                "tab_name": tab_name,
                "tab_slug": slugify(tab_name)
            }
            for url_name, tab_name in mapping.items()
        ]

        # write manifest file (atomic to avoid partial writes)
        target_dir = Path(settings.BASE_DIR) / "staticfiles" / "js"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "tab_manifest.json"

        try:
            tmp_file = target_file.with_suffix(".tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(listing, f, indent=2)
            os.replace(tmp_file, target_file)  # atomic swap
            print(f"✅ tab_manifest.json updated at {target_file}")
        except Exception as e:
            print(f"⚠️ Could not write tab_manifest.json: {e}")

        return JsonResponse(listing, safe=False)


def get_htmx_template_context(request, htmx_context):
    """
    Add HTMX-specific template context matching views.py patterns
    TESTING_TAG: TEMPLATE_CONTEXT_BUILDER
    """
    return {
        # Error handling context (matching handle_form_errors_htmx pattern)
        'htmx_error_container': htmx_context.get('htmx_target', '#main-content'),
        'htmx_success_container': htmx_context.get('htmx_target', '#main-content'),
        
        # Message handling (matching HTMXMessageMixin pattern)
        'htmx_message_target': '#messages' if htmx_context['htmx_target_is_main'] else htmx_context['htmx_target'],
        'htmx_show_messages': not htmx_context['htmx_target_is_modal'],  # Don't show messages in modals
        
        # Response enhancement flags (matching enhance_htmx_response pattern)
        'htmx_enhance_response': True,
        'htmx_add_triggers': True,
        
        # Redirect handling (matching smart_redirect pattern)  
        'htmx_redirect_mode': 'render' if htmx_context['htmx_target_is_main'] else 'location',
        'htmx_prevent_redirect': htmx_context['htmx_target_is_modal'],
    }
