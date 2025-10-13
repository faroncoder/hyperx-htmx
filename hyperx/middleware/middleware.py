"""
🚀 HyperX Middleware - HTMX's Sidekick ⚡
================================================================
Automatic HTMX and TabX processing middleware for Django.

MIT License - Copyright (c) 2025 Faron
https://github.com/faroncoder/hyperx-htmx
"""

import re, time, asyncio, logging
from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token
from django.utils.html import escape
# from hyperx.core.hx.hx_core import *
from hyperx.core.hx.hx_runtime_compiler import *
from hyperx.bin.cli.logger.hx_logger import *

# Import validate_htmx_request if available, or define a stub
try:
    # from hyperx.core.hx.htmx_validation import validate_htmx_request
    raise ImportError  # Force fallback to stub
except ImportError:
    def validate_htmx_request(request):
        # Basic validation stub; replace with actual logic as needed
        return True

_logger = load_logger("hyperx.middleware.middleware")
_logger_middleware = load_logger("hyperx.core.htmx_implementation.middleware")
_logger_security = load_logger("hyperx.core.htmx_implementation.security")
_logger_performance = load_logger("hyperx.core.htmx_implementation.performance")

from hyperx.bin.cli.utils.autodiscover import autodiscover

autodiscover('hyperx.templatetags.htmx_tags')  # ensure tags are loaded

# Define a stub for parse_xtab_header if not imported elsewhere
def parse_xtab_header(request):
    """
    Stub for parsing X-Tab header from request.
    Replace with actual implementation as needed.
    """
    xtab_header = request.headers.get("X-Tab")
    if xtab_header:
        # Example: parse key=value pairs separated by semicolons
        xtab = {}
        for pair in xtab_header.split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                xtab[k.strip()] = v.strip()
        return xtab
    return None




# ================================================================
# 🔹 HyperXMiddleware
# ================================================================
class HyperXMiddleware(MiddlewareMixin):
    """
    Handles automatic HTMX + TabX detection, CSRF injection,
    performance logging, and structured diagnostics.
    """

    def __init__(self, get_response):
        from django.conf import settings
        self.get_response = get_response
        self.config = getattr(settings, "HYPERX_MIDDLEWARE", {})

        # defaults
        self.auto_validate_htmx = self.config.get("AUTO_VALIDATE_HTMX", True)
        self.auto_parse_xtab = self.config.get("AUTO_PARSE_XTAB", True)
        self.security_logging = self.config.get("SECURITY_LOGGING", True)
        self.performance_tracking = self.config.get("PERFORMANCE_TRACKING", True)
        self.strict_xtab_validation = self.config.get("STRICT_XTAB_VALIDATION", False)

        _logger_middleware.info("HyperX Middleware initialized with config: %s", self.config)
        super().__init__(get_response)

    # ------------------------------------------------------------
    # Request Handling
    # ------------------------------------------------------------
    def process_request(self, request):
        """Attach htmx / xtab flags and start tracking."""
        try:
            request.htmx = self._detect_htmx_request(request) if self.auto_validate_htmx else False
            request.xtab = self._parse_xtab_header(request) if self.auto_parse_xtab else None

            # optional validation
            if self.auto_validate_htmx and request.htmx:
                valid = self._validate_htmx_request(request)
                if not valid:
                    _logger_security.warning(f"[HyperX] Invalid HTMX request blocked: {request.path}")
                    return HttpResponseBadRequest("Invalid HTMX request")

            if self.security_logging:
                self._log_security_info(request)

            if self.performance_tracking:
                request._hyperx_start_time = time.time()

        except Exception as e:
            _logger.error(f"process_request error: {e}", exc_info=True)
            return None

    def __call__(self, request):
        start_time = time.time() if self.performance_tracking else None
        self.process_request(request)
        response = self.get_response(request)
        response = self.process_response(request, response)

        if self.performance_tracking and start_time:
            duration = (time.time() - start_time) * 1000
            _logger_performance.debug(
                f"[HyperX] {request.method} {request.path} - {duration:.2f}ms "
                f"(HTMX={getattr(request, 'htmx', False)} XTab={bool(getattr(request, 'xtab', None))})"
            )
        return response

    def process_response(self, request, response):
        """Append HyperX headers, timing, and optional CSRF meta."""
        if asyncio.iscoroutine(response):
            return response

        response["X-HyperX-Processed"] = "true"

        if self.performance_tracking and hasattr(request, "_hyperx_start_time"):
            duration = time.time() - request._hyperx_start_time
            response["X-HyperX-Duration"] = f"{duration:.3f}s"

        # auto CSRF <meta> injection (safe for GET/HEAD)
        try:
            if request.method in ("GET", "HEAD") and "text/html" in response.get("Content-Type", ""):
                html = response.content.decode("utf-8")
                if not re.search(r'<meta\s+name=["\']csrf-token["\']', html, re.I):
                    token = get_token(request)
                    if token:
                        safe = escape(token)
                        snippet = f"""
<meta name="csrf-token" content="{safe}">
<script>
  document.body.dataset.csrf = "{safe}";
  if (window.htmx) {{
      htmx.config.headers["X-CSRFToken"] = "{safe}";
  }}
</script>
"""
                        html = re.sub(r"</head>", snippet + "</head>", html, flags=re.I)
                        response.content = html.encode("utf-8")
                        _logger.info("[HyperX] Auto-inserted CSRF meta/script.")
        except Exception as e:
            _logger.error(f"[HyperX] CSRF injection failed: {e}", exc_info=True)

        return response

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _detect_htmx_request(self, request):
        return (
            request.headers.get("HX-Request") == "true"
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )

    def _parse_xtab_header(self, request):
        try:
            xtab = parse_xtab_header(request)
            if xtab and self.strict_xtab_validation:
                if not all(xtab.get(k) for k in ["tab", "function", "command", "version"]):
                    _logger_security.warning(f"Incomplete X-Tab header: {xtab}")
                    return None
            return xtab
        except Exception as e:
            _logger_middleware.error(f"Error parsing X-Tab header: {e}")
            return None

    def _validate_htmx_request(self, request):
        try:
            return validate_htmx_request(request)
        except Exception as e:
            _logger_middleware.error(f"Error validating HTMX request: {e}")
            return False

    def _log_security_info(self, request):
        if request.htmx:
            _logger_security.info(
                f"HTMX request {request.method} {request.path} "
                f"IP={request.META.get('REMOTE_ADDR')} UA={request.META.get('HTTP_USER_AGENT', '')[:100]}"
            )


# ================================================================
# 🔹 HyperXSecurityMiddleware
# ================================================================
class HyperXSecurityMiddleware(MiddlewareMixin):
    """Extended security middleware for HyperX."""

    def __init__(self, get_response):
        from django.conf import settings
        self.get_response = get_response
        self.config = getattr(settings, "HYPERX_SECURITY", {})
        self.enable_rate_limiting = self.config.get("RATE_LIMITING", False)
        self.enable_pattern_detection = self.config.get("PATTERN_DETECTION", True)
        self.enable_auto_blocking = self.config.get("AUTO_BLOCKING", False)
        self.max_requests_per_minute = self.config.get("MAX_REQUESTS_PER_MINUTE", 60)
        _logger_security.info("HyperX Security Middleware initialized")
        super().__init__(get_response)

    def __call__(self, request):
        if not self._security_check(request):
            _logger_security.error(f"Security check failed for {request.path}")
            return HttpResponseBadRequest("Request blocked by HyperX security")
        return self.get_response(request)

    # ------------------------------------------------------------
    # Security Logic
    # ------------------------------------------------------------
    def _security_check(self, request):
        if self.enable_rate_limiting and hasattr(request, "htmx") and request.htmx:
            if not self._check_rate_limit(request):
                return False
        if self.enable_pattern_detection:
            if not self._check_patterns(request):
                return False
        if hasattr(request, "xtab") and request.xtab:
            if not self._validate_xtab_security(request):
                return False
        return True

    def _check_rate_limit(self, request):  # future placeholder
        return True

    def _check_patterns(self, request):
        suspicious = ["bot", "crawler", "spider", "scan"]
        ua = request.META.get("HTTP_USER_AGENT", "").lower()
        if any(p in ua for p in suspicious):
            _logger_security.warning(f"Suspicious UA detected: {ua}")
        return True

    def _validate_xtab_security(self, request):
        xtab = request.xtab or {}
        bad_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
        for field, value in xtab.items():
            if any(c in str(value) for c in bad_chars):
                _logger_security.error(f"X-Tab injection attempt: {field}={value}")
                return False
        return True
