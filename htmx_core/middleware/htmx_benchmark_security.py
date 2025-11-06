"""
HTMX Content Management Middleware
Handles automatic target div clearing and content management for HTMX requests
"""
from asyncio.log import logger
import json
import re
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import logging
import time
import re
# redirect import removed - using custom error responses instead
from django.contrib import messages 
from django.conf import settings



class HTMXContentMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response) 
    
    def process_request(self, request):
        """Process incoming HTMX requests and prepare for content management"""
        if self.is_htmx_request(request):
            # Store original target for later use
            request.htmx_target = request.headers.get('HX-Target', '')
            request.htmx_trigger = request.headers.get('HX-Trigger', '')
            request.htmx_current_url = request.headers.get('HX-Current-URL', '')

    def process_template_response(self, request, response):
        """Add HX-Trigger header for template responses if HTMX is present"""
        if getattr(request, "htmx", False):
            # Safe payload: browsers dispatch event with this detail
            payload = {"htmx:contentUpdated": {"source": "middleware"}}
            response["HX-Trigger"] = json.dumps(payload)
        return response
    
    def process_response(self, request, response):
        """Process HTMX responses and add auto-clearing functionality"""
        if not self.is_htmx_request(request):
            return response
            
        # Only process successful HTML responses
        if (response.status_code == 200 and 
            'text/html' in response.get('Content-Type', '')):
            
            target = getattr(request, 'htmx_target', '')
            
            if target:
                # Check if this is a converted redirect that needs forced clearing
                force_clear = getattr(request, 'htmx_clear_target', False)
                
                # Wrap content with auto-clearing functionality
                response = self.wrap_content_with_clearing(request, response, target, force_clear)
                
                # Add HTMX headers for better UX
                self.add_htmx_headers(response, request)
        
        return response
    
    def is_htmx_request(self, request):
        """Check if request is from HTMX"""
        return request.headers.get('HX-Request') == 'true'
    
    def wrap_content_with_clearing(self, request, response, target, force_clear=False):
        """Wrap response content with auto-clearing functionality"""
        try:
            original_content = response.content.decode('utf-8')
            
            # Create the clearing script and wrapper
            clearing_wrapper = self.create_clearing_wrapper(target, original_content, force_clear)
            
            # Create new response with wrapped content
            new_response = HttpResponse(
                clearing_wrapper,
                content_type=response['Content-Type'],
                status=response.status_code
            )
            
            # Copy original headers
            for header, value in response.items():
                if header.lower() not in ['content-length', 'content-encoding']:
                    new_response[header] = value
            
            return new_response
            
        except Exception as e:
            # If wrapping fails, return original response
            logger = logging.getLogger(__name__)
            logger.warning("HTMX Middleware Error: %s", e)
            return response
    
    def create_clearing_wrapper(self, target, content, force_clear=False):
        """Create the wrapper with clearing functionality"""
        # Sanitize target for use in JavaScript
        safe_target = self.sanitize_target(target)
        
        # Generate unique ID for this update

        update_id = f"htmx_update_{int(time.time() * 1000)}"
        
        # Determine clearing behavior
        clear_method = 'force' if force_clear else 'smooth'
        
        wrapper = f"""
        <div id="{update_id}" style="display: none;">
            {content}
        </div>

        <script>
        (function() {{
            // Auto-clear and update function
            function clearAndUpdate() {{
                const targetElement = document.querySelector('{safe_target}');
                const newContent = document.getElementById('{update_id}');
                
                if (targetElement && newContent) {{
                    // Determine clearing method
                    const clearMethod = '{clear_method}';
                    
                    if (clearMethod === 'force') {{
                        // Force clear immediately (for redirects)
                        console.log('HTMX: Force clearing target due to redirect conversion');
                        targetElement.classList.add('htmx-loading');
                        
                        // Immediate clear and replace
                        targetElement.innerHTML = '';
                        targetElement.innerHTML = newContent.innerHTML;
                        targetElement.classList.remove('htmx-loading');
                        
                        // Clean up and reinitialize
                        newContent.remove();
                        reinitializeComponents(targetElement);
                        
                        // Trigger events
                        targetElement.dispatchEvent(new CustomEvent('htmx:contentUpdated', {{
                            detail: {{
                                target: '{safe_target}',
                                updateId: '{update_id}',
                                method: 'force',
                                redirectConverted: true
                            }}
                        }}));
                    }} else {{
                        // Smooth clear (default behavior)
                        targetElement.classList.add('htmx-loading');
                        
                        // Clear existing content with fade effect
                        targetElement.style.transition = 'opacity 0.2s ease';
                        targetElement.style.opacity = '0';
                        
                        setTimeout(() => {{
                            // Clear the target completely
                            targetElement.innerHTML = '';
                            
                            // Move new content to target
                            targetElement.innerHTML = newContent.innerHTML;
                            
                            // Remove loading state and fade in
                            targetElement.style.opacity = '1';
                            targetElement.classList.remove('htmx-loading');
                            
                            // Clean up temporary content
                            newContent.remove();
                            
                            // Reinitialize components
                            reinitializeComponents(targetElement);
                            
                            // Trigger custom event for other scripts
                            targetElement.dispatchEvent(new CustomEvent('htmx:contentUpdated', {{
                                detail: {{
                                    target: '{safe_target}',
                                    updateId: '{update_id}',
                                    method: 'smooth'
                                }}
                            }}));
                        }}, 200);
                    }}
                }} else {{
                    console.warn('HTMX Middleware: Target element not found:', '{safe_target}');
                    // Fallback: just show the content
                    if (newContent) {{
                        newContent.style.display = 'block';
                    }}
                }}
            }}
            
            // Component reinitialization function
            function reinitializeComponents(targetElement) {{
                // Re-initialize any JavaScript that might be needed
                if (typeof window.reinitializeScripts === 'function') {{
                    window.reinitializeScripts(targetElement);
                }}
                
                // Restart feather icons if present
                if (typeof feather !== 'undefined') {{
                    feather.replace();
                }}
                
                // Re-initialize Bootstrap tooltips and popovers
                if (typeof bootstrap !== 'undefined') {{
                    // Initialize tooltips
                    const tooltips = targetElement.querySelectorAll('[data-bs-toggle="tooltip"]:not(.tooltip-initialized)');
                    tooltips.forEach(el => {{
                        new bootstrap.Tooltip(el);
                        el.classList.add('tooltip-initialized');
                    }});
                    
                    // Initialize popovers
                    const popovers = targetElement.querySelectorAll('[data-bs-toggle="popover"]:not(.popover-initialized)');
                    popovers.forEach(el => {{
                        new bootstrap.Popover(el);
                        el.classList.add('popover-initialized');
                    }});
                }}
            }}
            
            // Execute immediately if DOM is ready, otherwise wait
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', clearAndUpdate);
            }} else {{
                clearAndUpdate();
            }}
        }})();
        </script>
        """
        return wrapper
        
    def sanitize_target(self, target):
        """Sanitize target selector for safe use in JavaScript"""
        if not target:
            return '#main-content'  # Default fallback
        
        # Remove any potentially dangerous characters
        # Keep only valid CSS selector characters
        safe_target = re.sub(r'[^a-zA-Z0-9#.\-_\s\[\]=":]', '', target)
        
        # Ensure it starts with a valid selector
        if not safe_target.startswith(('#', '.', '[')):
            safe_target = f'#{safe_target}'
            
        return safe_target
    
    def add_htmx_headers(self, response, request):
        """Add helpful HTMX headers for better UX"""
        # Add HX-Trigger header for client-side events
        triggers = {}
        
        # Always add contentUpdated trigger for HTMX responses
        triggers['contentUpdated'] = True
        
        # Add htmx:contentUpdated for compatibility with HTMX expectations
        triggers['htmx:contentUpdated'] = True
        
        # Add any custom triggers from the view
        if hasattr(response, 'htmx_trigger'):
            if isinstance(response.htmx_trigger, list):
                for trigger in response.htmx_trigger:
                    triggers[trigger] = True
            elif isinstance(response.htmx_trigger, dict):
                triggers.update(response.htmx_trigger)
            else:
                triggers[response.htmx_trigger] = True
        
        # Always set HX-Trigger header for HTMX responses
        response['HX-Trigger'] = json.dumps(triggers)
        
        # Add refresh indicator if needed
        if getattr(request, 'htmx_refresh_needed', False):
            response['HX-Refresh'] = 'true'
        
        # Add location header for navigation if set
        if hasattr(response, 'htmx_location'):
            response['HX-Location'] = response.htmx_location

class HTMXErrorMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response) 
    
    def process_exception(self, request, exception):
        """Handle exceptions in HTMX requests"""
        if self.is_htmx_request(request):
            # Return a user-friendly error message for HTMX requests
            error_html = f"""
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Error:</strong> Something went wrong while processing your request.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        """
            return HttpResponse(error_html, status=500)
        
        # Let Django handle non-HTMX errors normally
        return None
    
    def is_htmx_request(self, request):
        """Check if request is from HTMX"""
        return request.headers.get('HX-Request') == 'true'


class HTMXLoadingMiddleware(MiddlewareMixin):
   
    def __init__(self, get_response=None):
        super().__init__(get_response) 
    
    
    def process_response(self, request, response):
        """Add loading indicators for HTMX responses"""
        if (self.is_htmx_request(request) and 
            response.status_code == 200 and 
            'text/html' in response.get('Content-Type', '')):
            
            # Add loading CSS if not already present
            if not self.has_loading_css(response):
                response = self.add_loading_css(response)
        
        return response
    
    def is_htmx_request(self, request):
        """Check if request is from HTMX"""
        return request.headers.get('HX-Request') == 'true'
    
    def has_loading_css(self, response):
        """Check if response already has loading CSS"""
        try:
            content = response.content.decode('utf-8')
            return 'htmx-loading' in content
        except:
            return True  # Assume it has it to avoid errors
    
    def add_loading_css(self, response):
        """Add loading CSS to response"""
        try:
            content = response.content.decode('utf-8')
            
            loading_css = """
            <style>
            .htmx-loading {
                position: relative;
                overflow: hidden;
            }

            .htmx-loading::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }

            .htmx-loading::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 24px;
                height: 24px;
                margin: -12px 0 0 -12px;
                border: 2px solid #ccc;
                border-top-color: #007bff;
                border-radius: 50%;
                animation: htmx-spin 1s linear infinite;
                z-index: 1001;
            }

            @keyframes htmx-spin {
                to {
                    transform: rotate(360deg);
                }
            }
            </style>
            """
        
            # Add CSS to the beginning of content
            enhanced_content = loading_css + content
            
            new_response = HttpResponse(
                enhanced_content,
                content_type=response['Content-Type'],
                status=response.status_code
            )
            
            # Copy headers
            for header, value in response.items():
                if header.lower() not in ['content-length', 'content-encoding']:
                    new_response[header] = value
            
            return new_response
        
        except Exception as e:
            print(f"Loading CSS Middleware Error: {e}")
            return response


class HTMXSecurityMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response=None):
        super().__init__(get_response)  # ✅ this line ensures async_mode is defined
        self.protected_patterns = getattr(settings, "HTMX_PROTECTED_ENDPOINTS", [])
        self.redirect_auth = getattr(settings, "HTMX_REDIRECT_AUTH", None)
        self.redirect_anon = getattr(settings, "HTMX_REDIRECT_ANON", None)

    def process_request(self, request):
        # HTMX requests are always allowed
        if self.is_htmx_request(request):
            return None
        # Non-HTMX requests on protected paths are redirected
        if any(re.match(p, request.path) for p in self.protected_patterns):
            return self.redirect_to_safety(request)
        return None

    @staticmethod
    def is_htmx_request(request):
        return request.headers.get("HX-Request") == "true"

    def redirect_to_safety(self, request):
        if hasattr(request, "user") and request.user.is_authenticated:
            if self.redirect_auth:
                messages.warning(
                    request,
                    "Direct URL access to HTMX endpoints is not allowed. "
                    "Please use the in-page navigation.",
                )
                # SNUBBED: redirect(self.redirect_auth) -> Custom error response
                from django.http import HttpResponse
                return HttpResponse(
                    "<h3>Access Denied</h3><p>Direct URL access to HTMX endpoints is not allowed.</p>",
                    status=403,
                    content_type='text/html'
                )
        if self.redirect_anon:
            messages.error(request, "Please log in to continue.")
            # SNUBBED: redirect(self.redirect_anon) -> Custom error response
            from django.http import HttpResponse
            return HttpResponse(
                "<h3>Authentication Required</h3><p>Please log in to continue.</p>",
                status=401,
                content_type='text/html'
            )
        return None  # Fallback: do nothing if no redirect defined


class HTMXBenchmarkMiddleware(MiddlewareMixin):
    """
    HTMX Benchmark and Performance Analytics Middleware
    Provides performance monitoring, timing, and analytics for HTMX requests
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = logging.getLogger(__name__)
        self.performance_metrics = {}
        
    def process_request(self, request):
        """Start timing and collect request metrics"""
        if self.is_htmx_request(request):
            request._htmx_start_time = time.time()
            request._htmx_metrics = {
                'request_method': request.method,
                'content_length': request.META.get('CONTENT_LENGTH', 0),
                'target': request.headers.get('HX-Target', ''),
                'trigger': request.headers.get('HX-Trigger', ''),
                'current_url': request.headers.get('HX-Current-URL', ''),
                'request_path': request.path,
            }
    
    def process_response(self, request, response):
        """Complete timing and log performance metrics"""
        if (hasattr(request, '_htmx_start_time') and 
            self.is_htmx_request(request)):
            
            # Calculate response time
            end_time = time.time()
            response_time = end_time - request._htmx_start_time
            
            # Collect response metrics
            metrics = request._htmx_metrics
            metrics.update({
                'response_time_ms': round(response_time * 1000, 2),
                'status_code': response.status_code,
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
                'content_type': response.get('Content-Type', ''),
                'timestamp': time.time(),
            })
            
            # Store metrics for analysis
            path = request.path
            if path not in self.performance_metrics:
                self.performance_metrics[path] = []
            
            self.performance_metrics[path].append(metrics)
            
            # Keep only last 100 requests per path to avoid memory issues
            if len(self.performance_metrics[path]) > 100:
                self.performance_metrics[path] = self.performance_metrics[path][-100:]
            
            # Add performance headers
            response['X-HTMX-Response-Time'] = f"{metrics['response_time_ms']}ms"
            response['X-HTMX-Request-Size'] = str(metrics['content_length'])
            response['X-HTMX-Response-Size'] = str(metrics['response_size'])
            
            # Log slow requests (over 500ms)
            if response_time > 0.5:
                self.logger.warning(
                    f"Slow HTMX request: {request.path} took {response_time:.2f}s "
                    f"(Target: {metrics['target']}, Trigger: {metrics['trigger']})"
                )
            
            # Log performance info for debugging
            self.logger.debug(
                f"HTMX Performance: {request.path} - "
                f"{metrics['response_time_ms']}ms, "
                f"Status: {metrics['status_code']}, "
                f"Size: {metrics['response_size']} bytes"
            )
        
        return response
    
    def get_performance_summary(self, path=None):
        """Get performance summary for analysis"""
        if path:
            metrics_list = self.performance_metrics.get(path, [])
        else:
            metrics_list = []
            for path_metrics in self.performance_metrics.values():
                metrics_list.extend(path_metrics)
        
        if not metrics_list:
            return None
        
        response_times = [m['response_time_ms'] for m in metrics_list]
        
        return {
            'total_requests': len(metrics_list),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'slow_requests': len([t for t in response_times if t > 500]),
            'paths_tracked': len(self.performance_metrics),
        }
    
    def is_htmx_request(self, request):
        """Check if request is an HTMX request"""
        return (
            request.headers.get("HX-Request") == "true" or
            hasattr(request, 'htmx') and request.htmx
        )