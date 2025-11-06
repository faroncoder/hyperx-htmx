"""
URL Security Middleware
Strips URLs and prevents URL exposure in responses
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import re


class URLSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to hide URLs and prevent URL leakage
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.hide_urls = getattr(settings, 'HTMX_HIDE_URLS', False)
        self.strip_urls = getattr(settings, 'HTMX_STRIP_URLS_FROM_RESPONSE', False)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Remove URL-related headers from incoming requests"""
        if self.hide_urls:
            # Remove URL-exposing headers
            headers_to_remove = [
                'HTTP_HX_CURRENT_URL',
                'HTTP_HX_HISTORY_RESTORE_REQUEST',
                'HTTP_REFERER',
            ]
            
            for header in headers_to_remove:
                if header in request.META:
                    del request.META[header]
        
        return None
    
    def process_response(self, request, response):
        """Strip URLs from response content and headers"""
        if not self.hide_urls:
            return response
        
        # Remove URL-exposing response headers
        headers_to_remove = [
            'HX-Push-Url',
            'HX-Replace-Url',
            'HX-Location',
            'Location'
        ]
        
        for header in headers_to_remove:
            if header in response:
                del response[header]
        
        # Strip URLs from response content if it's HTML/text
        if (hasattr(response, 'content') and 
            response.get('Content-Type', '').startswith(('text/', 'application/json'))):
            
            content = response.content.decode('utf-8', errors='ignore')
            
            if self.strip_urls:
                # Remove common URL patterns (be careful not to break functionality)
                url_patterns = [
                    r'data-hx-push-url="[^"]*"',
                    r'hx-push-url="[^"]*"',
                    r'data-hx-replace-url="[^"]*"',
                    r'hx-replace-url="[^"]*"',
                ]
                
                for pattern in url_patterns:
                    content = re.sub(pattern, '', content)
            
            response.content = content.encode('utf-8')
        
        # Add security headers
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response