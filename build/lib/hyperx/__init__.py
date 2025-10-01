"""
🚀 HyperX - HTMX's Sidekick ⚡
================================================================

TabX so fast! The ultimate HTMX enhancement protocol for Django.

MIT License - Copyright (c) 2025 Faron
https://github.com/faroncoder/hyperx-htmx

HyperX provides a comprehensive HTMX integration system featuring:
- Lightning-fast TabX protocol (X-Tab system)  
- Attribute generation and parsing
- Security validation and authentication
- Response helpers and decorators
- Performance monitoring and logging
"""

__version__ = "1.0.0"
__author__ = "Faron"
__email__ = "faron@example.com"
__license__ = "MIT"
__url__ = "https://github.com/faroncoder/hyperx-htmx"

# Main imports for easy access
from .core import (
    # Core attribute building
    build_htmx_attrs,
    
    # Form helpers
    htmx_form_submit,
    htmx_infinite_scroll,
    
    # Request validation
    validate_htmx_request,
    is_htmx_request,
    render_htmx,
    
    # Response helpers
    hx_redirect,
    hx_refresh,
    hx_location,
    hx_push_url,
    hx_replace_url,
    hx_retarget,
    hx_reswap,
    hx_trigger,
    
    # Authentication
    htmx_login_required,
    
    # TabX Protocol
    parse_xtab_header,
    validate_xtab_request,
    xtab_required,
)

# Middleware imports
from .middleware import (
    HyperXMiddleware,
    HyperXSecurityMiddleware,
    add_hyperx_to_request,
)

__all__ = [
    # Core functionality
    'build_htmx_attrs',
    'htmx_form_submit', 
    'htmx_infinite_scroll',
    'validate_htmx_request',
    'is_htmx_request',
    'render_htmx',
    
    # Response helpers
    'hx_redirect',
    'hx_refresh', 
    'hx_location',
    'hx_push_url',
    'hx_replace_url',
    'hx_retarget',
    'hx_reswap',
    'hx_trigger',
    
    # Authentication & Security
    'htmx_login_required',
    
    # TabX Protocol (Lightning Fast!)
    'parse_xtab_header',
    'validate_xtab_request', 
    'xtab_required',
    
    # Middleware
    'HyperXMiddleware',
    'HyperXSecurityMiddleware',
    'add_hyperx_to_request',
    
    # Package info
    '__version__',
    '__author__',
    '__license__',
    '__url__',
]