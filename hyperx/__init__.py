"""
HyperX – HTMX
Declarative <hx:*> + TabX protocol for Django.
MIT © 2025 Faroncoder
https://github.com/faroncoder/hyperx-htmx
"""

from __future__ import annotations
import logging

__version__ = "3.0.0"
__author__ = "Jeff Panasuik (Faroncoder)"
__email__ = "jeff.panasuik@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/faroncoder/hyperx-htmx"

# ---------------------------------------------------------------------
# Lightweight logging so imports stay safe during Django startup
# ---------------------------------------------------------------------
_logger = logging.getLogger("hyperx")
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)

_logger.info(f"✅ HyperX {__version__} package imported")

# ---------------------------------------------------------------------
# Public API (imported lazily to avoid circular startup issues)
# ---------------------------------------------------------------------
def __getattr__(name: str):
    """
    Lazy import pattern: only load heavy modules when accessed.
    Prevents InvalidTemplateLibrary / settings-premature errors.
    """
    if name in {
        "build_htmx_attrs",
        "htmx_form_submit",
        "htmx_infinite_scroll",
        "validate_htmx_request",
        "is_htmx_request",
        "render_htmx",
        "hx_redirect",
        "hx_refresh",
        "hx_location",
        "hx_push_url",
        "hx_replace_url",
        "hx_retarget",
        "hx_reswap",
        "hx_trigger",
        "htmx_login_required",
        "parse_xtab_header",
        "validate_xtab_request",
        "xtab_required",
        "HyperXMiddleware",
        "HyperXSecurityMiddleware",
        "HyperXInstaller",
        "install_hyperx",
    }:
        from importlib import import_module
        mod = import_module("hyperx.core.core")
        return getattr(mod, name)
    raise AttributeError(name)

# ---------------------------------------------------------------------
# Django app configuration hook
# ---------------------------------------------------------------------
try:
    from .apps import HyperXConfig
except Exception:
    HyperXConfig = None
