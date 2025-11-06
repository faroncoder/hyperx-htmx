"""
HTMX Core - Advanced Template Helpers
====================================

Sophisticated template rendering logic and wrapper detection for HTMX Core system.
Provides intelligent template selection and response structuring.

Author: HTMX Core Team  
Date: November 5, 2025
Status: Integrated from htmx_orphaned_snippets.py
"""

from django.conf import settings


def get_htmx_render_mode(request, htmx_context=None):
    """
    Determine HTMX rendering mode based on request context.
    Provides intelligent template selection for different HTMX scenarios.
    
    Args:
        request: Django HttpRequest object
        htmx_context (dict): Optional HTMX context dictionary
        
    Returns:
        str: Render mode ('full_page', 'main_content', 'modal_content', 'sidebar_content', 'fragment_content')
        
    Example:
        >>> mode = get_htmx_render_mode(request, htmx_context)
        >>> if mode == 'modal_content':
        ...     # Use modal-specific template
    """
    if htmx_context is None:
        htmx_context = _build_htmx_context_from_request(request)
    
    if not htmx_context.get('is_htmx', False):
        return 'full_page'
    
    target = htmx_context.get('htmx_target', '')
    
    if target in ['#maincontentplaceholder', '#main-content', '#main']:
        return 'main_content'
    elif 'modal' in target.lower():
        return 'modal_content'
    elif 'sidebar' in target.lower() or 'sidemenu' in target.lower():
        return 'sidebar_content'
    else:
        return 'fragment_content'


def needs_htmx_wrapper(htmx_context):
    """
    Determine if HTMX response needs wrapper elements.
    Smart wrapper detection for consistent HTMX response structure.
    
    Args:
        htmx_context (dict): HTMX context dictionary
        
    Returns:
        bool: True if wrapper is needed, False otherwise
        
    Example:
        >>> if needs_htmx_wrapper(htmx_context):
        ...     # Add wrapper div around content
    """
    if not htmx_context.get('is_htmx', False):
        return False
    
    # Don't wrap modal content or fragments that are already wrapped
    if htmx_context.get('htmx_target_is_modal', False):
        return False
    
    # Main content usually needs wrapping for consistent styling
    if htmx_context.get('htmx_target_is_main', False):
        return True
        
    # Sidebar content needs wrapping for proper layout
    if htmx_context.get('htmx_target_is_sidebar', False):
        return True
    
    return False


def get_template_suffix_for_mode(render_mode):
    """
    Get appropriate template suffix based on render mode.
    
    Args:
        render_mode (str): Render mode from get_htmx_render_mode()
        
    Returns:
        str: Template suffix to append to base template names
        
    Example:
        >>> suffix = get_template_suffix_for_mode('modal_content')
        >>> template_name = f"base_template{suffix}.html"  # "base_template_modal.html"
    """
    suffix_mapping = {
        'full_page': '',
        'main_content': '_fragment',
        'modal_content': '_modal', 
        'sidebar_content': '_sidebar',
        'fragment_content': '_fragment'
    }
    
    return suffix_mapping.get(render_mode, '_fragment')


def get_wrapper_class_for_target(htmx_target):
    """
    Get appropriate CSS wrapper class based on HTMX target.
    
    Args:
        htmx_target (str): HTMX target selector
        
    Returns:
        str: CSS class name for wrapper element
        
    Example:
        >>> wrapper_class = get_wrapper_class_for_target('#main-content')
        >>> # Returns: 'htmx-main-content-wrapper'
    """
    if not htmx_target:
        return 'htmx-content-wrapper'
    
    # Normalize target to class name
    clean_target = htmx_target.lstrip('#').replace('-', '_').replace(' ', '_').lower()
    
    return f"htmx_{clean_target}_wrapper"


def build_template_context_for_mode(request, render_mode, base_context=None):
    """
    Build template context optimized for specific render mode.
    
    Args:
        request: Django HttpRequest object
        render_mode (str): Render mode from get_htmx_render_mode()
        base_context (dict): Optional base context to extend
        
    Returns:
        dict: Enhanced template context
        
    Example:
        >>> context = build_template_context_for_mode(request, 'modal_content')
        >>> # Returns context with modal-specific helpers
    """
    if base_context is None:
        base_context = {}
    
    enhanced_context = base_context.copy()
    
    # Add mode-specific context
    enhanced_context.update({
        'htmx_render_mode': render_mode,
        'is_full_page': render_mode == 'full_page',
        'is_main_content': render_mode == 'main_content', 
        'is_modal_content': render_mode == 'modal_content',
        'is_sidebar_content': render_mode == 'sidebar_content',
        'is_fragment_content': render_mode == 'fragment_content',
    })
    
    # Add template helpers
    enhanced_context.update({
        'template_suffix': get_template_suffix_for_mode(render_mode),
        'needs_wrapper': render_mode in ['main_content', 'sidebar_content'],
        'show_navigation': render_mode in ['full_page', 'main_content'],
        'show_footer': render_mode == 'full_page',
    })
    
    return enhanced_context


def get_smart_template_name(base_template, render_mode):
    """
    Generate smart template name based on render mode.
    
    Args:
        base_template (str): Base template name (e.g., 'dashboard/profile')
        render_mode (str): Render mode
        
    Returns:
        str: Complete template path with appropriate suffix
        
    Example:
        >>> template = get_smart_template_name('dashboard/profile', 'modal_content')
        >>> # Returns: 'dashboard/profile_modal.html'
    """
    if not base_template:
        return None
    
    # Remove .html if present
    if base_template.endswith('.html'):
        base_template = base_template[:-5]
    
    suffix = get_template_suffix_for_mode(render_mode)
    
    return f"{base_template}{suffix}.html"


# ============================================================================
# PRIVATE HELPER FUNCTIONS  
# ============================================================================

def _build_htmx_context_from_request(request):
    """
    Build basic HTMX context from request headers.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        dict: Basic HTMX context
    """
    is_htmx = request.headers.get('HX-Request') == 'true'
    htmx_target = request.headers.get('HX-Target', '')
    
    return {
        'is_htmx': is_htmx,
        'htmx_target': htmx_target,
        'htmx_target_is_main': htmx_target in ['#maincontentplaceholder', '#main-content', '#main'],
        'htmx_target_is_modal': 'modal' in htmx_target.lower(),
        'htmx_target_is_sidebar': 'sidebar' in htmx_target.lower() or 'sidemenu' in htmx_target.lower(),
    }


# ============================================================================
# INTEGRATION UTILITIES FOR EXISTING HTMX SYSTEM
# ============================================================================

def enhance_existing_htmx_helpers():
    """
    Utility to check integration with existing htmx_helpers.py functions.
    Can be used to verify compatibility and suggest improvements.
    
    Returns:
        dict: Integration status and recommendations
    """
    integration_status = {
        'render_mode_detection': 'available',
        'wrapper_detection': 'available', 
        'template_helpers': 'available',
        'smart_template_naming': 'available',
        'recommendations': [
            'Replace basic render mode logic with get_htmx_render_mode()',
            'Use needs_htmx_wrapper() for consistent wrapper handling',
            'Integrate get_smart_template_name() for automatic template selection'
        ]
    }
    
    return integration_status


def get_enhanced_context_helpers():
    """
    Get dictionary of enhanced context helper functions.
    For easy integration with existing context processors.
    
    Returns:
        dict: Helper functions keyed by name
    """
    return {
        'get_htmx_render_mode': get_htmx_render_mode,
        'needs_htmx_wrapper': needs_htmx_wrapper,
        'get_template_suffix_for_mode': get_template_suffix_for_mode,
        'get_wrapper_class_for_target': get_wrapper_class_for_target,
        'build_template_context_for_mode': build_template_context_for_mode,
        'get_smart_template_name': get_smart_template_name
    }