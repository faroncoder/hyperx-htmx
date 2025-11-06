from django.conf import settings
import json
from functools import wraps
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# redirect import removed - using HTMX client-side redirects instead
from django.urls import reverse

# NOTE: PREFIX constant moved to htmx_orphaned_snippets.py for testing

def is_htmx_request(request, template_name, context=None, status=200):
    """
    Renders a template for HTMX requests, falling back to normal render if not HTMX.
    NOTE: This is an alias for render_htmx for backward compatibility
    """
    return render_htmx(request, template_name, context, status)

def render_htmx(request, template_name, context=None, status=200):
    """
    Renders a template for HTMX requests, falling back to normal render if not HTMX.
    """
    context = context or {}
    if getattr(request, "htmx", False) or request.headers.get("HX-Request") == "true":
        return render(request, template_name, context=context, status=status)
    return render(request, template_name, context=context, status=status)


def _hx_redirect(url: str) -> HttpResponse:
    resp = HttpResponse("")
    resp["HX-Redirect"] = url
    return resp


# Alias for compatibility
hx_redirect = _hx_redirect


def add_htmx_trigger(response, trigger_name, data=None):
    """
    Add HTMX trigger to response
    """
    if not hasattr(response, '_htmx_triggers'):
        response._htmx_triggers = []
    
    if data:
        response._htmx_triggers.append({trigger_name: data})
    else:
        response._htmx_triggers.append(trigger_name)
    
    return response


def hx_trigger(event_name: str, payload=None, status=200):
    resp = HttpResponse(status=status)
    # Accept either a single event or a dict of events
    if isinstance(event_name, dict):
        # Merge all events into HX-Trigger
        resp["HX-Trigger"] = json.dumps(event_name)
    else:
        resp["HX-Trigger"] = json.dumps({event_name: payload} if payload is not None else event_name)
    return resp



# Custom login_required that does NOT append ?next= - REDIRECT NEUTRALIZED
def login_required_no_next(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # SNUBBED: redirect(settings.LOGIN_URL) -> HTMX client-side redirect
            return _hx_redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# HTMX-aware login_required that shows login form inline instead of redirecting
def htmx_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Check if this is an HTMX request
            if request.headers.get('HX-Request') == 'true':
                # Instead of redirecting, return the login form HTML using HTMX defaults
                from htmx_core.functions.auth_forms import LoginForm
                from htmx_core.utils.htmx_defaults import htmx_defaults
                
                # Get HTMX defaults for proper targeting and headers
                htmx_context = htmx_defaults(request, divplaceholder="#maincontentplaceholder")
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
                    return render(request, 'auth/login.html', context)
                except Exception as e:
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
                                            <a href="{reverse('access_login')}" 
                                               class="btn btn-primary"
                                               hx-get="{reverse('access_view')}" 
                                               hx-target="#{{ htmx_context.get('divplaceholder') }}">
                                                <i class="fas fa-sign-in-alt me-2"></i>Sign In
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                    return HttpResponse(html_content)
            else:
                # For non-HTMX requests, redirect to our login page
                try:
                    return render(request, 'auth/login.html', {})
                except:
                    # Fallback if reverse fails
                    return render(request, 'auth/login.html', {})
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_dynamic_context(request, base_context):
    """
    Get request-specific context that shouldn't be cached with enhanced HTMX analysis
    TESTING_TAG: DYNAMIC_CONTEXT_ANALYZER
    """
    # Enhanced HTMX-specific context (compliant with htmx_core rules)
    is_htmx = request.headers.get('HX-Request') == 'true'  # Exact match like views.py
    htmx_target = request.headers.get('HX-Target', '')
    
    htmx_context = {
        'is_htmx_request': is_htmx,
        'is_htmx': is_htmx,  # Alternative name used in views.py
        'htmx_target': htmx_target,
        'htmx_trigger': request.headers.get('HX-Trigger', ''),
        'htmx_current_url': request.headers.get('HX-Current-URL', ''),
        
        # Additional HTMX context from views.py patterns
        'htmx_boosted': request.headers.get('HX-Boosted') == 'true',
        'htmx_history_restore': request.headers.get('HX-History-Restore-Request') == 'true',
        'htmx_prompt': request.headers.get('HX-Prompt', ''),
        
        # Target analysis (from middleware patterns)
        'htmx_target_is_main': htmx_target in ['#maincontentplaceholder', '#main-content', '#main'],
        'htmx_target_is_modal': 'modal' in htmx_target.lower(),
        'htmx_target_is_sidebar': 'sidebar' in htmx_target.lower() or 'sidemenu' in htmx_target.lower(),
        
        # Content management flags (from middleware)
        'htmx_needs_clearing': getattr(request, 'htmx_clear_target', False),
        'htmx_force_refresh': getattr(request, 'htmx_refresh_needed', False),
    }
    
    # Dynamically determine active tab using enhanced detection system
    try:
        from htmx_core.utils.htmx_tab_detection import get_tab_context_for_request
        
        tab_context = get_tab_context_for_request(request)
        tab_active = tab_context.get('tab_active', 'dashboard')
        tab_active_slug = tab_context.get('tab_active_slug', 'dashboard')
    except ImportError:
        tab_active = 'dashboard'  # fallback
        tab_active_slug = 'dashboard'

    # Template helper functions using enhanced template system
    try:
        from htmx_core.utils.htmx_template_helpers import get_htmx_render_mode, needs_htmx_wrapper, get_template_suffix_for_mode
        
        render_mode = get_htmx_render_mode(request, htmx_context)
        template_helpers = {
            'htmx_render_mode': render_mode,
            'htmx_template_suffix': get_template_suffix_for_mode(render_mode),
            'htmx_wrapper_needed': needs_htmx_wrapper(htmx_context),
        }
    except ImportError:
        # Fallback to basic template helpers
        template_helpers = {
            'htmx_render_mode': _get_htmx_render_mode(request, htmx_context),
            'htmx_template_suffix': '_fragment' if is_htmx else '',
            'htmx_wrapper_needed': _needs_htmx_wrapper(htmx_context),
        }
    
    return {
        **htmx_context,
        **template_helpers,
        'tab_active': tab_active,
        'tab_active_slug': tab_active_slug,
    }


def _get_htmx_render_mode(request, htmx_context):
    """
    Determine HTMX rendering mode based on request context
    TESTING_TAG: RENDER_MODE_DETECTION
    """
    if not htmx_context['is_htmx']:
        return 'full_page'
    
    target = htmx_context['htmx_target']
    
    if target in ['#maincontentplaceholder', '#main-content', 'main']:
        return 'main_content'
    elif 'modal' in target.lower():
        return 'modal_content'
    elif 'sidebar' in target.lower() or 'sidemenu' in target.lower():
        return 'sidebar_content'
    else:
        return 'fragment_content'


def _needs_htmx_wrapper(htmx_context):
    """
    Determine if HTMX response needs wrapper elements
    TESTING_TAG: WRAPPER_DETECTION
    """
    # Don't wrap modal content or fragments that are already wrapped
    if htmx_context['htmx_target_is_modal']:
        return False
    
    # Main content usually needs wrapping for consistent styling
    if htmx_context['htmx_target_is_main']:
        return True
        
    # Sidebar content needs wrapping for proper layout
    if htmx_context['htmx_target_is_sidebar']:
        return True
    
    return False


# ============================================================================
# ORPHANED SNIPPETS MOVED TO COLLECTION FILE
# ============================================================================
# All commented template functions, duplicate helpers, and unused constants
# have been moved to htmx_core/utils/htmx_orphaned_snippets.py for systematic
# testing and evaluation.
#
# To test orphaned snippets:
# 1. Import htmx_orphaned_snippets 
# 2. Set ENABLE_[SNIPPET_NAME] = True
# 3. Test functionality and document results
# 4. Move useful snippets back to appropriate locations

