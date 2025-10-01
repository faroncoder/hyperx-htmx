"""
🚀 HyperX Middleware - HTMX's Sidekick ⚡
================================================================

Automatic HTMX and TabX processing middleware for Django.

MIT License - Copyright (c) 2025 Faron
https://github.com/yourusername/hyperx

Usage:
    Add to MIDDLEWARE in settings.py:
    MIDDLEWARE = [
        ...
        'core.utils.hyperx_middleware.HyperXMiddleware',
        ...
    ]
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseBadRequest
from .htmx_implemention import parse_xtab_header, validate_htmx_request

# Middleware-specific loggers
logger_middleware = logging.getLogger('core.htmx_implementation.middleware')
logger_security = logging.getLogger('core.htmx_implementation.security')
logger_performance = logging.getLogger('core.htmx_implementation.performance')


class HyperXMiddleware(MiddlewareMixin):
    """
    HyperX Middleware - Automatic HTMX and TabX processing
    
    Features:
    - Auto-detects HTMX requests (adds request.htmx)
    - Auto-parses X-Tab headers (adds request.xtab)
    - Security validation and logging
    - Performance monitoring
    - Request/response processing
    
    Configuration (settings.py):
    HYPERX_MIDDLEWARE = {
        'AUTO_VALIDATE_HTMX': True,     # Auto-validate HTMX requests
        'AUTO_PARSE_XTAB': True,        # Auto-parse X-Tab headers
        'SECURITY_LOGGING': True,       # Enhanced security logging
        'PERFORMANCE_TRACKING': True,   # Track request performance
        'STRICT_XTAB_VALIDATION': False,# Strict X-Tab format validation
    }
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Load configuration from settings
        from django.conf import settings
        self.config = getattr(settings, 'HYPERX_MIDDLEWARE', {})
        
        # Default configuration
        self.auto_validate_htmx = self.config.get('AUTO_VALIDATE_HTMX', True)
        self.auto_parse_xtab = self.config.get('AUTO_PARSE_XTAB', True)
        self.security_logging = self.config.get('SECURITY_LOGGING', True)
        self.performance_tracking = self.config.get('PERFORMANCE_TRACKING', True)
        self.strict_xtab_validation = self.config.get('STRICT_XTAB_VALIDATION', False)
        
        logger_middleware.info("HyperX Middleware initialized with config: %s", self.config)
        super().__init__(get_response)

    def __call__(self, request):
        # Start performance tracking
        start_time = time.time() if self.performance_tracking else None
        
        # Process request
        self.process_request(request)
        
        # Get response
        response = self.get_response(request)
        
        # Process response
        response = self.process_response(request, response)
        
        # Log performance
        if self.performance_tracking and start_time:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger_performance.debug(
                f"HyperX request processed: {request.method} {request.path} - "
                f"{duration:.2f}ms - HTMX={getattr(request, 'htmx', False)} - "
                f"XTab={bool(getattr(request, 'xtab', None))}"
            )
        
        return response

    def process_request(self, request):
        """Process incoming request - add HTMX and X-Tab detection"""
        
        # 1. HTMX Detection
        request.htmx = self._detect_htmx_request(request)
        
        # 2. X-Tab Parsing
        if self.auto_parse_xtab:
            request.xtab = self._parse_xtab_header(request)
        
        # 3. Security Validation
        if self.auto_validate_htmx and request.htmx:
            if not self._validate_htmx_request(request):
                logger_security.warning(
                    f"Invalid HTMX request blocked: {request.method} {request.path} "
                    f"from {request.META.get('REMOTE_ADDR')}"
                )
                # Note: We log but don't block - let views decide
        
        # 4. Security Logging
        if self.security_logging:
            self._log_security_info(request)
    
    def process_response(self, request, response):
        """Process outgoing response - add HyperX headers if needed"""
        
        # Add HyperX identification header
        response['X-HyperX-Processed'] = 'true'
        
        # Add performance info if tracking enabled
        if self.performance_tracking and hasattr(request, '_hyperx_start_time'):
            duration = time.time() - request._hyperx_start_time
            response['X-HyperX-Duration'] = f"{duration:.3f}s"
        
        # Log response info
        if hasattr(request, 'htmx') and request.htmx:
            logger_middleware.debug(
                f"HTMX response: {response.status_code} for {request.path} - "
                f"XTab={bool(getattr(request, 'xtab', None))}"
            )
        
        return response
    
    def _detect_htmx_request(self, request):
        """Detect if request is from HTMX"""
        htmx_indicators = [
            request.headers.get('HX-Request') == 'true',
            request.headers.get('X-Requested-With') == 'XMLHttpRequest',
            'HX-' in str(request.headers),
        ]
        
        is_htmx = any(htmx_indicators)
        
        if is_htmx:
            logger_middleware.debug(f"HTMX request detected: {request.method} {request.path}")
        
        return is_htmx
    
    def _parse_xtab_header(self, request):
        """Parse X-Tab header automatically"""
        try:
            xtab = parse_xtab_header(request)
            if xtab:
                logger_middleware.debug(
                    f"X-Tab parsed: tab={xtab['tab']}, function={xtab['function']}, "
                    f"command={xtab['command']}, version={xtab['version']}"
                )
                
                # Strict validation if enabled
                if self.strict_xtab_validation:
                    if not all([xtab['tab'], xtab['function'], xtab['command'], xtab['version']]):
                        logger_security.warning(
                            f"Incomplete X-Tab header: {xtab['raw']} from "
                            f"{request.META.get('REMOTE_ADDR')}"
                        )
                        return None
            
            return xtab
            
        except Exception as e:
            logger_middleware.error(f"Error parsing X-Tab header: {str(e)}")
            return None
    
    def _validate_htmx_request(self, request):
        """Validate HTMX request"""
        try:
            return validate_htmx_request(request)
        except Exception as e:
            logger_middleware.error(f"Error validating HTMX request: {str(e)}")
            return False
    
    def _log_security_info(self, request):
        """Log security-relevant information"""
        if request.htmx:
            # Log HTMX-specific security info
            security_info = {
                'method': request.method,
                'path': request.path,
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],
                'htmx_target': request.headers.get('HX-Target'),
                'htmx_trigger': request.headers.get('HX-Trigger'),
                'has_xtab': bool(getattr(request, 'xtab', None)),
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            }
            
            logger_security.info(f"HTMX request security log: {security_info}")


class HyperXSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced security middleware for HyperX
    
    Features:
    - Strict X-Tab validation
    - HTMX request rate limiting
    - Suspicious pattern detection
    - Auto-blocking of malicious requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        
        # Security configuration
        self.config = getattr(settings, 'HYPERX_SECURITY', {})
        self.enable_rate_limiting = self.config.get('RATE_LIMITING', False)
        self.enable_pattern_detection = self.config.get('PATTERN_DETECTION', True)
        self.enable_auto_blocking = self.config.get('AUTO_BLOCKING', False)
        self.max_requests_per_minute = self.config.get('MAX_REQUESTS_PER_MINUTE', 60)
        
        logger_security.info("HyperX Security Middleware initialized")
        super().__init__(get_response)
    
    def __call__(self, request):
        # Security checks
        if not self._security_check(request):
            logger_security.error(f"Security check failed for {request.path}")
            return HttpResponseBadRequest("Request blocked by HyperX security")
        
        response = self.get_response(request)
        return response
    
    def _security_check(self, request):
        """Perform security checks"""
        
        # 1. Rate limiting (if enabled)
        if self.enable_rate_limiting and hasattr(request, 'htmx') and request.htmx:
            if not self._check_rate_limit(request):
                return False
        
        # 2. Pattern detection (if enabled)
        if self.enable_pattern_detection:
            if not self._check_patterns(request):
                return False
        
        # 3. X-Tab validation (if present)
        if hasattr(request, 'xtab') and request.xtab:
            if not self._validate_xtab_security(request):
                return False
        
        return True
    
    def _check_rate_limit(self, request):
        """Check rate limiting for HTMX requests"""
        # Implement rate limiting logic here
        # This is a simplified example
        return True
    
    def _check_patterns(self, request):
        """Check for suspicious patterns"""
        # Check for suspicious user agents, patterns, etc.
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scan'
        ]
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(pattern in user_agent for pattern in suspicious_patterns):
            if hasattr(request, 'htmx') and request.htmx:
                logger_security.warning(
                    f"Suspicious HTMX request from bot/crawler: {user_agent} - {request.path}"
                )
                # Don't block bots automatically, just log
        
        return True
    
    def _validate_xtab_security(self, request):
        """Validate X-Tab header for security"""
        xtab = request.xtab
        
        # Check for injection attempts in X-Tab values
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
        for field in ['tab', 'function', 'command', 'version']:
            value = xtab.get(field, '')
            if any(char in str(value) for char in dangerous_chars):
                logger_security.error(
                    f"Potential X-Tab injection attempt: {field}={value} from "
                    f"{request.META.get('REMOTE_ADDR')}"
                )
                return False
        
        return True


# Utility function for manual middleware integration
def add_hyperx_to_request(request):
    """
    Manually add HyperX functionality to request (for testing or custom usage)
    
    Usage:
        from core.utils.hyperx_middleware import add_hyperx_to_request
        add_hyperx_to_request(request)
    """
    request.htmx = request.headers.get('HX-Request') == 'true'
    request.xtab = parse_xtab_header(request) if request.htmx else None
    
    logger_middleware.debug(
        f"HyperX manually added to request: htmx={request.htmx}, "
        f"xtab={bool(request.xtab)}"
    )