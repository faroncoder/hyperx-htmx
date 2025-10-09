"""
🚀 HyperX - HTMX 
================================================================
TabX so fast! The ultimate HTMX enhancement protocol for Django.

MIT License - Copyright (c) 2025 Faron
https://github.com/faroncoder/hyperx-htmx

Features:
- Lightning-fast TabX protocol (X-Tab system)
- Declarative <hx:*> Template Tag Compiler
- Attribute generation and parsing
- Security validation and authentication
- Response helpers and decorators
- Performance monitoring and logging
- Live Dataset Watcher + AI Schema Autogen (optional)
"""

from __future__ import annotations
import sys
import importlib
import logging

from pathlib import Path

__version__ = "3.0.0"
__author__ = "Faroncoder"
__email__ = "jeff.panasuik@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/faroncoder/hyperx-htmx"

# ─────────────────────────────────────────────
# 🧱 Core Imports
# ─────────────────────────────────────────────
from .core.core import (
    build_htmx_attrs,
    htmx_form_submit,
    htmx_infinite_scroll,
    validate_htmx_request,
    is_htmx_request,
    render_htmx,
    hx_redirect,
    hx_refresh,
    hx_location,
    hx_push_url,
    hx_replace_url,
    hx_retarget,
    hx_reswap,
    hx_trigger,
    htmx_login_required,
    parse_xtab_header,
    validate_xtab_request,
    xtab_required,
 
)

# ─────────────────────────────────────────────
# 🧠 Middleware
# ─────────────────────────────────────────────
from .middleware import (
    HyperXMiddleware,
    HyperXSecurityMiddleware,
)

# ─────────────────────────────────────────────
# 🧩 Elements Autoload
# ─────────────────────────────────────────────
try:
    import hyperx_elements  # auto-discovers declarative <hx:*> components
    ELEMENTS_REGISTERED = True
except Exception as e:
    ELEMENTS_REGISTERED = False
    logging.getLogger("hyperx").warning(f"[HyperX] Elements library not loaded: {e}")

# ─────────────────────────────────────────────
# 🧠 Auto-Installer Integration
# ─────────────────────────────────────────────
    



# ─────────────────────────────────────────────
# 🧩 Optional AI + Dataset Watcher
# ─────────────────────────────────────────────
try:
    from .opt.hyperx.ai_schema_autogen import *  # noqa
    AI_TOOLS_AVAILABLE = True
except ImportError:
    AI_TOOLS_AVAILABLE = False

try:
    from .opt.hyperx.dataset_watch_service import *  # noqa
    WATCHER_AVAILABLE = True
except ImportError:
    WATCHER_AVAILABLE = False

# ─────────────────────────────────────────────
# 🧭 Logging Initialization
# ─────────────────────────────────────────────
_logger = logging.getLogger("hyperx")
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)

_logger.info(f"✅ HyperX {__version__} initialized")
_logger.info(f"   🧩 Elements Registered: {ELEMENTS_REGISTERED}")
_logger.info(f"   🧠 AI Tools: {AI_TOOLS_AVAILABLE}")
_logger.info(f"   👁️ Watcher: {WATCHER_AVAILABLE}")

# ─────────────────────────────────────────────
# 🔖 Public API
# ─────────────────────────────────────────────
__all__ = [
    # Core functionality
    "build_htmx_attrs",
    "htmx_form_submit",
    "htmx_infinite_scroll",
    "validate_htmx_request",
    "is_htmx_request",
    "render_htmx",
    # Response helpers
    "hx_redirect",
    "hx_refresh",
    "hx_location",
    "hx_push_url",
    "hx_replace_url",
    "hx_retarget",
    "hx_reswap",
    "hx_trigger",
    # Authentication
    "htmx_login_required",
    # TabX
    "parse_xtab_header",
    "validate_xtab_request",
    "xtab_required",
    # Middleware
    "HyperXMiddleware",
    "HyperXSecurityMiddleware",
    # Auto-installer
    "install_hyperx",
    "HyperXInstaller",
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__url__",
]


default_app_config = "hyperx.apps.HyperXConfig"

from .core.core import *


from .autodiscover  import autodiscover 



   