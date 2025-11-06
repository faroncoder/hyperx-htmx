"""
HTMX Core - Advanced Tab Detection System
========================================

Intelligent tab detection and URL analysis for HTMX Core X-Tab system.
Provides sophisticated tab extraction from Django URL patterns and request paths.

Author: HTMX Core Team
Date: November 5, 2025
Status: Integrated from _to_be_review_htmx_system.py
"""

import re
from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
from django.urls import resolve
from pathlib import Path


def get_active_tab_from_url(request):
    """
    Dynamically determine active tab from URL resolver.
    Automatically compiles tab mapping from Django's URL patterns.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        str: Active tab name or None if not detected
        
    Example:
        >>> request.path = '/dashboard/profile/'
        >>> get_active_tab_from_url(request)
        'profile'
    """
    try:
        # Get the resolved URL info
        resolved = resolve(request.path)
        url_name = resolved.url_name
        namespace = resolved.namespace
        
        # Full URL name with namespace
        full_url_name = f"{namespace}:{url_name}" if namespace else url_name
        
        # Get or build dynamic tab mapping from URL patterns
        tab_mapping = _get_dynamic_tab_mapping()
        
        # Check exact match first
        if full_url_name in tab_mapping:
            return tab_mapping[full_url_name]
        
        # Smart pattern extraction from URL name
        tab = _extract_tab_from_url_name(url_name, namespace)
        if tab:
            return tab
            
        # Path-based analysis as fallback
        return _extract_tab_from_path(request.path)
        
    except Exception as e:
        # Fallback to simple path-based detection
        print(f"Active tab detection error: {e}")
        return _fallback_tab_detection(request.path)


def slugify_tab_name(tab_name):
    """
    Convert any tab name into a URL/DOM-safe slug.
    
    Args:
        tab_name (str): Raw tab name
        
    Returns:
        str: Slugified tab name or None if input is empty
        
    Example:
        >>> slugify_tab_name("User Profile")
        'user-profile'
    """
    if not tab_name:
        return None
    # Prefer Django's slugify (lowercase, hyphenate)
    return slugify(tab_name)


def extract_tab_from_pattern_name(url_name, namespace=''):
    """
    Extract tab name from URL pattern name using intelligent analysis.
    
    Args:
        url_name (str): Django URL pattern name
        namespace (str): URL namespace
        
    Returns:
        str: Extracted tab name or None
        
    Example:
        >>> extract_tab_from_pattern_name('admin_users', 'dashboard')
        'admin_users'
    """
    if not url_name:
        return None
    
    # Define tab extraction rules (these work for any app/namespace)
    extraction_rules = [
        # Direct matches (exact name becomes tab)
        (r'^(profile|billing|security|notifications|config|settings|dashboard)$', lambda m: m.group(1)),
        
        # Prefixed patterns (ind_, org_, admin_, user_, etc.)
        (r'^(\w+)_(profile|billing|security|notifications|config|settings|dashboard|management|audit|staffing)$', 
         lambda m: f"{m.group(1)}_{m.group(2)}"),
        
        # Suffixed patterns (profile_edit, billing_view, etc.)
        (r'^(profile|billing|security|notifications|config|settings|dashboard)_(\w+)$', 
         lambda m: m.group(1)),
        
        # Account/management patterns
        (r'^account[_-](\w+)$', lambda m: m.group(1)),
        (r'^manage[_-](\w+)$', lambda m: f"manage_{m.group(1)}"),
        (r'^admin[_-](\w+)$', lambda m: f"admin_{m.group(1)}"),
        
        # API patterns (group related APIs under same tab)
        (r'^api[_-](\w+)[_-](\w+)$', lambda m: m.group(1)),  # api_user_status -> user
        (r'^(\w+)[_-]api$', lambda m: m.group(1)),  # user_api -> user
        
        # Dashboard/analysis patterns
        (r'^(\w+)[_-](dashboard|analysis|overview)$', lambda m: m.group(1)),
        (r'^(dashboard|analysis|overview)[_-](\w+)$', lambda m: m.group(2)),
        
        # Generic patterns (try to extract meaningful part)
        (r'^(\w+)[_-](\w+)[_-](\w+)$', lambda m: m.group(1)),  # Take first part of compound names
    ]
    
    # Apply extraction rules
    for pattern, extractor in extraction_rules:
        match = re.match(pattern, url_name, re.IGNORECASE)
        if match:
            try:
                result = extractor(match)
                if result and result not in ['view', 'edit', 'create', 'update', 'delete', 'list']:
                    return result
            except:
                continue
    
    # Fallback: check if name contains common tab keywords
    tab_keywords = ['profile', 'billing', 'security', 'notifications', 'config', 
                   'settings', 'dashboard', 'management', 'audit', 'staffing', 'analysis']
    
    url_lower = url_name.lower()
    for keyword in tab_keywords:
        if keyword in url_lower:
            # Try to extract prefix if it exists
            parts = url_name.lower().split('_')
            if len(parts) > 1 and keyword in parts:
                keyword_index = parts.index(keyword)
                if keyword_index > 0:
                    return f"{parts[0]}_{keyword}"
                else:
                    return keyword
            return keyword
    
    return None


# ============================================================================
# PRIVATE HELPER FUNCTIONS
# ============================================================================

def _get_dynamic_tab_mapping():
    """
    Dynamically build tab mapping by analyzing Django's URL patterns.
    Caches the result for performance.
    
    Returns:
        dict: Mapping of URL names to tab names
    """
    # Check cache first (30 minute cache for URL patterns)
    cache_key = 'htmx_core_dynamic_tab_mapping'
    cached_mapping = cache.get(cache_key)
    if cached_mapping and not getattr(settings, 'DEBUG', False):
        return cached_mapping
    
    try:
        from django.urls import get_resolver
        from django.urls.resolvers import URLPattern, URLResolver
        
        # Get the root URL resolver
        root_resolver = get_resolver()
        tab_mapping = {}
        
        # Recursively analyze URL patterns
        _analyze_url_patterns(root_resolver.url_patterns, tab_mapping, '')
        
        # Cache the mapping (30 minutes in production, no cache in debug)
        if not getattr(settings, 'DEBUG', False):
            cache.set(cache_key, tab_mapping, 1800)
        
        return tab_mapping
        
    except Exception as e:
        print(f"Error building dynamic tab mapping: {e}")
        return {}


def _analyze_url_patterns(patterns, tab_mapping, namespace_prefix=''):
    """
    Recursively analyze URL patterns to build tab mapping.
    
    Args:
        patterns: Django URL patterns list
        tab_mapping (dict): Dictionary to populate with mappings
        namespace_prefix (str): Current namespace prefix
    """
    from django.urls.resolvers import URLPattern, URLResolver
    
    for pattern in patterns:
        try:
            if isinstance(pattern, URLResolver):
                # Handle URL includes (nested patterns)
                new_namespace = f"{namespace_prefix}{pattern.namespace}:" if pattern.namespace else namespace_prefix
                _analyze_url_patterns(pattern.url_patterns, tab_mapping, new_namespace)
                
            elif isinstance(pattern, URLPattern):
                # Handle individual URL patterns
                if hasattr(pattern, 'name') and pattern.name:
                    full_name = f"{namespace_prefix}{pattern.name}"
                    
                    # Extract tab info from URL name using intelligent patterns
                    tab = extract_tab_from_pattern_name(pattern.name, namespace_prefix.rstrip(':'))
                    
                    if tab:
                        tab_mapping[full_name] = tab
                        
        except Exception as e:
            # Skip problematic patterns but don't fail completely
            print(f"Error analyzing pattern: {e}")
            continue


def _extract_tab_from_url_name(url_name, namespace):
    """
    Extract tab from URL name with namespace consideration.
    
    Args:
        url_name (str): URL pattern name
        namespace (str): URL namespace
        
    Returns:
        str: Extracted tab name
    """
    return extract_tab_from_pattern_name(url_name, namespace)


def _extract_tab_from_path(path):
    """
    Extract tab from URL path when pattern matching fails.
    
    Args:
        path (str): URL path
        
    Returns:
        str: Extracted tab name or None
    """
    if not path or path == '/':
        return None
    
    # Clean and split path
    path_parts = [part for part in path.strip('/').split('/') if part]
    
    if not path_parts:
        return None
    
    # Look for meaningful parts in reverse order (most specific first)
    for i in range(len(path_parts) - 1, -1, -1):
        part = path_parts[i]
        
        # Skip common non-tab parts
        if part.lower() in ['view', 'edit', 'create', 'update', 'delete', 'list', 'detail']:
            continue
            
        # Check if this part looks like a tab
        tab_result = extract_tab_from_pattern_name(part)
        if tab_result:
            return tab_result
            
        # Check for compound parts (profile-edit, billing_view, etc.)
        if '_' in part or '-' in part:
            separator = '_' if '_' in part else '-'
            sub_parts = part.split(separator)
            for sub_part in sub_parts:
                tab_result = extract_tab_from_pattern_name(sub_part)
                if tab_result:
                    return tab_result
    
    # Final fallback: return the last meaningful part
    if len(path_parts) >= 2:
        return path_parts[-1].replace('-', '_')
    
    return None


def _fallback_tab_detection(path):
    """
    Simple fallback tab detection for when URL resolver fails.
    Works with any app structure, not just specific apps.
    
    Args:
        path (str): URL path
        
    Returns:
        str: Detected tab name or None
    """
    if not path or path == '/':
        return None
        
    # Use the same path extraction logic as above
    return _extract_tab_from_path(path)


# ============================================================================
# INTEGRATION UTILITIES
# ============================================================================

def get_tab_context_for_request(request):
    """
    Get complete tab context for a request.
    Convenience function for templates and views.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        dict: Tab context with active tab and slug
        
    Example:
        >>> context = get_tab_context_for_request(request)
        >>> context
        {'tab_active': 'profile', 'tab_active_slug': 'profile'}
    """
    tab_active = get_active_tab_from_url(request)
    tab_active_slug = slugify_tab_name(tab_active)
    
    return {
        'tab_active': tab_active,
        'tab_active_slug': tab_active_slug,
    }


def debug_tab_detection(request, verbose=True):
    """
    Debug utility to analyze tab detection for a specific request.
    
    Args:
        request: Django HttpRequest object
        verbose (bool): Whether to print detailed analysis
        
    Returns:
        dict: Debug information about tab detection
    """
    try:
        resolved = resolve(request.path)
        url_name = resolved.url_name
        namespace = resolved.namespace
    except:
        resolved = None
        url_name = None
        namespace = None
    
    tab_active = get_active_tab_from_url(request)
    tab_slug = slugify_tab_name(tab_active)
    
    debug_info = {
        'request_path': request.path,
        'resolved_url_name': url_name,
        'resolved_namespace': namespace,
        'detected_tab': tab_active,
        'tab_slug': tab_slug,
        'detection_method': 'unknown'
    }
    
    if verbose:
        print("=== Tab Detection Debug ===")
        for key, value in debug_info.items():
            print(f"{key}: {value}")
    
    return debug_info