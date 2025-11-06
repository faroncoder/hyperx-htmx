"""
HTMX View Helpers
Simplified helpers and decorators for HTMX requests.
"""
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import resolve
from functools import wraps
import json
from htmx_core.utils.htmx_x_tab_registry import TabRegistry
from htmx_core.utils.htmx_helpers import get_dynamic_context


def htmx_redirect(url, force_clear=True):
    """
    Create an HTMX-compatible redirect response
    
    Args:
        url: URL to redirect to
        force_clear: Whether to clear browser cache (default True)
    
    Returns:
        HttpResponseRedirect: Standard redirect response that will be processed by htmx_response decorator
    """
    return HttpResponseRedirect(url)



def htmx_response(view_func):
    """
    Decorator to enhance views for HTMX compatibility
    Automatically handles HTMX-specific response features and converts redirects to renders
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get the original response
        response = view_func(request, *args, **kwargs)
        
        # If it's an HTMX request, enhance the response
        if request.headers.get('HX-Request') == 'true':
            # Check if response is a redirect and convert it
            if isinstance(response, HttpResponseRedirect):
                response = handle_htmx_redirect(request, response)
            
            # Add HTMX-specific headers and features
            if hasattr(response, 'content'):
                # Store original target for middleware
                request.htmx_target = request.headers.get('HX-Target', '')
                
                # Add custom HTMX attributes to response
                response = enhance_htmx_response(request, response)
        
        return response
    
    return wrapper


def handle_htmx_redirect(request, redirect_response):
    """
    Convert redirect response to render response for HTMX requests
    This maintains SPA behavior while handling redirects gracefully
    """
    redirect_url = redirect_response.url
    
    try:
        # Parse the redirect URL to determine the target view
        redirect_info = parse_redirect_url(request, redirect_url)
        
        if redirect_info['is_internal']:
            # Internal redirect - render the target view directly
            return render_redirect_target(request, redirect_info)
        else:
            # External redirect - use HX-Location header for client-side redirect
            response = HttpResponse('')
            response['HX-Location'] = redirect_url
            add_htmx_trigger(response, 'externalRedirect', {'url': redirect_url})
            return response
            
    except Exception as e:
        # Fallback: use HX-Location for any redirect we can't handle
        print(f"HTMX Redirect Error: {e}")
        response = HttpResponse('')
        response['HX-Location'] = redirect_url
        add_htmx_trigger(response, 'redirectFallback', {'url': redirect_url, 'error': str(e)})
        return response


def parse_redirect_url(request, redirect_url):
    """
    Parse redirect URL to determine if it's internal and what view it targets
    """
    from django.contrib.sites.shortcuts import get_current_site
    
    # Get current site info
    current_site = get_current_site(request)
    current_domain = current_site.domain
    
    # Check if URL is relative or absolute internal
    is_internal = False
    clean_url = redirect_url
    
    if redirect_url.startswith('/'):
        # Relative URL - definitely internal
        is_internal = True
        clean_url = redirect_url
    elif redirect_url.startswith(('http://', 'https://')):
        # Absolute URL - check if it's our domain
        if current_domain in redirect_url:
            is_internal = True
            # Extract path from full URL
            import urllib.parse
            parsed = urllib.parse.urlparse(redirect_url)
            clean_url = parsed.path
            if parsed.query:
                clean_url += '?' + parsed.query
        else:
            is_internal = False
    else:
        # Assume relative if no scheme
        is_internal = True
        clean_url = '/' + redirect_url.lstrip('/')
    
    redirect_info = {
        'is_internal': is_internal,
        'url': redirect_url,
        'clean_url': clean_url,
        'view_name': None,
        'view_args': [],
        'view_kwargs': {},
        'namespace': None
    }
    
    # If internal, try to resolve the view
    if is_internal:
        try:
            # Remove query string for URL resolution
            path_only = clean_url.split('?')[0]
            resolved = resolve(path_only)
            redirect_info.update({
                'view_name': resolved.view_name,
                'view_args': resolved.args,
                'view_kwargs': resolved.kwargs,
                'namespace': resolved.namespace,
                'url_name': resolved.url_name,
            })
        except Exception as e:
            print(f"Could not resolve redirect URL {clean_url}: {e}")
    
    return redirect_info


def render_redirect_target(request, redirect_info):
    """
    Render the target of a redirect directly instead of redirecting
    """
    try:
        # Import the view function and call it directly
        view_func = resolve(redirect_info['clean_url'].split('?')[0]).func
        
        # Create a new request with the redirect URL parameters
        redirect_request = create_redirect_request(request, redirect_info)
        
        # Call the target view function
        response = view_func(
            redirect_request, 
            *redirect_info['view_args'], 
            **redirect_info['view_kwargs']
        )
        
        # Add metadata to indicate this was a redirect conversion
        if hasattr(response, 'content'):
            add_htmx_trigger(response, 'redirectConverted', {
                'original_url': redirect_info['url'],
                'view_name': redirect_info['view_name']
            })
            # Mark for target clearing in middleware (always force clear for redirects)
            redirect_request.htmx_clear_target = True
            
            # Log successful conversion
            log_redirect_conversion(
                redirect_info['url'], 
                redirect_info.get('view_name', 'unknown'),
                success=True
            )
        
        return response
        
    except Exception as e:
        # Log failed conversion
        log_redirect_conversion(
            redirect_info['url'], 
            redirect_info.get('view_name', 'unknown'),
            success=False, 
            error=str(e)
        )
        
        # Fallback to HX-Location
        response = HttpResponse('')
        response['HX-Location'] = redirect_info['url']
        add_htmx_trigger(response, 'redirectRenderError', {
            'url': redirect_info['url'],
            'error': str(e)
        })
        return response


def create_redirect_request(original_request, redirect_info):
    """
    Create a new request object for the redirect target with proper parameters
    """
    # Create a copy of the original request
    redirect_request = original_request.__class__(original_request.environ.copy())
    
    # Copy important attributes
    redirect_request.user = original_request.user
    redirect_request.session = original_request.session
    redirect_request.META = original_request.META.copy()
    redirect_request.method = original_request.method
    redirect_request.content_type = original_request.content_type
    
    # Update path and query string
    if '?' in redirect_info['clean_url']:
        path, query_string = redirect_info['clean_url'].split('?', 1)
        redirect_request.path = path
        redirect_request.path_info = path
        redirect_request.META['QUERY_STRING'] = query_string
        
        # Parse query parameters
        from django.http import QueryDict
        redirect_request.GET = QueryDict(query_string)
    else:
        redirect_request.path = redirect_info['clean_url']
        redirect_request.path_info = redirect_info['clean_url']
        redirect_request.GET = QueryDict()
    
    # Copy POST data if applicable
    redirect_request.POST = original_request.POST.copy()
    redirect_request.FILES = original_request.FILES.copy()
    
    # Maintain HTMX headers
    htmx_headers = {
        'HX-Request': 'true',
        'HX-Target': original_request.headers.get('HX-Target', ''),
        'HX-Trigger': original_request.headers.get('HX-Trigger', ''),
        'HX-Current-URL': original_request.headers.get('HX-Current-URL', ''),
    }
    
    for key, value in htmx_headers.items():
        if value:
            redirect_request.META[f'HTTP_{key.replace("-", "_").upper()}'] = value
    
    return redirect_request


def enhance_htmx_response(request, response):
    """
    Enhance response for HTMX requests
    """
    # Add custom headers for better UX
    if hasattr(response, '__setitem__'):  # Check if it's an HttpResponse
        # Add trigger events
        triggers = getattr(response, '_htmx_triggers', [])
        if triggers:
            response['HX-Trigger'] = json.dumps({trigger: True for trigger in triggers})
        
        # Add location header if needed
        if hasattr(response, '_htmx_location'):
            response['HX-Location'] = response._htmx_location
        
        # Add refresh header if needed
        if getattr(response, '_htmx_refresh', False):
            response['HX-Refresh'] = 'true'
    
    return response



def htmx_render(request, template_name, context=None, **kwargs):
    """
    Enhanced render function for HTMX requests.
    Adds header-based HTMX context and lazily loads dynamic reflection data.
    Automatically handles fragment templates and enhances response metadata.
    """
    if context is None:
        context = {}

    # 1️⃣ Basic HTMX header context (fast path)
    is_htmx = request.headers.get('HX-Request') == 'true'
    context.update({
        'is_htmx': is_htmx,
        'htmx_target': request.headers.get('HX-Target', ''),
        'htmx_trigger': request.headers.get('HX-Trigger', ''),
        'htmx_current_url': request.headers.get('HX-Current-URL', ''),
    })

    # 2️⃣ Lazy reflection context (only computed when needed)
    if is_htmx:
        try:
            dynamic_ctx = get_dynamic_context(request, context)
            context.update(dynamic_ctx)
        except Exception as e:
            if getattr(request, 'DEBUG', False) or getattr(request, 'settings', None):
                print(f"⚠️  HTMX dynamic context load error: {e}")

    # 3️⃣ Fragment template detection (HTMX partials)
    if is_htmx:
        fragment_template = template_name.replace('.html', '_fragment.html')
        try:
            from django.template.loader import get_template
            get_template(fragment_template)
            template_name = fragment_template
        except Exception:
            pass  # fall back silently to original template

    # 4️⃣ Standard render
    response = render(request, template_name, context, **kwargs)

    # 5️⃣ Final response enhancement for HTMX
    if is_htmx:
        response = enhance_htmx_response(request, response)

    return response




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


def set_htmx_location(response, url):
    """
    Set HTMX location for client-side navigation
    """
    response._htmx_location = url
    return response


def set_htmx_refresh(response):
    """
    Set HTMX refresh flag
    """
    response._htmx_refresh = True
    return response



def htmx_only(view_func):
    """
    Decorator to ensure view only accepts HTMX requests
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.headers.get('HX-Request') != 'true':
            return HttpResponse('This endpoint only accepts HTMX requests', status=400)
        return view_func(request, *args, **kwargs)
    
    return wrapper


def handle_form_errors_htmx(form, request):
    """
    Helper to handle form errors in HTMX context
    """
    if form.errors:
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    error_list.append(error)
                else:
                    field_label = form[field].label or field
                    error_list.append(f"{field_label}: {error}")
        
        error_message = '. '.join(error_list)
        
        # Create error response for HTMX
        error_html = f'''
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Validation Error:</strong> {error_message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        '''
        
        response = HttpResponse(error_html)
        add_htmx_trigger(response, 'formError', {'errors': form.errors})
        return response
    
    return None


def create_htmx_success_response(message, redirect_url=None, refresh=False):
    """
    Create a standardized success response for HTMX requests
    """
    success_html = f'''
    <div class="alert alert-success alert-dismissible fade show" role="alert">
        <i class="fas fa-check-circle me-2"></i>
        <strong>Success:</strong> {message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    '''
    
    response = HttpResponse(success_html)
    add_htmx_trigger(response, 'actionSuccess', {'message': message})
    
    if redirect_url:
        set_htmx_location(response, redirect_url)
    
    if refresh:
        set_htmx_refresh(response)
    
    return response








def log_redirect_conversion(original_url, target_view, success=True, error=None):
    """
    Log redirect conversion for debugging
    """
    status = "SUCCESS" if success else "FAILED"
    print(f"HTMX Redirect Conversion [{status}]: {original_url} -> {target_view}")
    if error:
        print(f"  Error: {error}")



    
    


def lazy_tab_map(request):
    """Expose mapping only when fetched (lazy load)."""
    registry = TabRegistry()
    return JsonResponse(registry.generate_tab_manifest())


