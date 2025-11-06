# htmx_core/tab_reflector.py
from django.urls import get_resolver, URLResolver, URLPattern
from django.core.cache import cache
from django.conf import settings
import logging
import json
from pathlib import Path

# Import enhanced tab detection system
from htmx_core.utils.htmx_tab_detection import (
    get_active_tab_from_url, 
    slugify_tab_name,
    get_tab_context_for_request,
    debug_tab_detection
)

logger = logging.getLogger(__name__)
_TAB_MAPPING = None   # in-memory cache


def _analyze_url_patterns(patterns, tab_mapping, namespace_prefix=""):
    for pattern in patterns:
        try:
            if isinstance(pattern, URLResolver):
                ns = f"{namespace_prefix}{pattern.namespace}:" if pattern.namespace else namespace_prefix
                _analyze_url_patterns(pattern.url_patterns, tab_mapping, ns)
            elif isinstance(pattern, URLPattern) and pattern.name:
                full_name = f"{namespace_prefix}{pattern.name}"
                tab_mapping[full_name] = _extract_tab_from_pattern_name(pattern.name, namespace_prefix.rstrip(":"))
        except Exception as e:
            logger.warning("Error analyzing pattern %s: %s", pattern, e)

def _extract_tab_from_pattern_name(name, namespace):
    """Your naming logic → tab key"""
    return name.split("_")[0] if "_" in name else name

def get_tab_mapping():
    """Public accessor used at runtime."""
    global _TAB_MAPPING
    if _TAB_MAPPING:
        return _TAB_MAPPING
    mapping = cache.get("dynamic_tab_mapping")
    if mapping:
        _TAB_MAPPING = mapping
        return mapping
    mapping = build_tab_mapping()
    cache.set("dynamic_tab_mapping", mapping, None)
    _TAB_MAPPING = mapping
    return mapping




DECLARATIVE_FILE = Path(settings.BASE_DIR) / "staticfiles" / "json" / "tabname_declarative.json"

def _load_declarative_tabnames():
    """Load manual tab-name overrides from JSON if present."""
    if not DECLARATIVE_FILE.exists():
        return {}
    try:
        with open(DECLARATIVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Could not read {DECLARATIVE_FILE}: {e}")
        return {}

def _extract_tab_from_path(path):
    """
    Extract tab from URL path when pattern matching fails
    TESTING_TAG: TAB_PATH_EXTRACTION
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
        tab_result = _extract_tab_from_pattern_name(part, "")
        if tab_result:
            return tab_result
            
        # Check for compound parts (profile-edit, billing_view, etc.)
        if '_' in part or '-' in part:
            separator = '_' if '_' in part else '-'
            sub_parts = part.split(separator)
            for sub_part in sub_parts:
                tab_result = _extract_tab_from_pattern_name(sub_part, "")
                if tab_result:
                    return tab_result
    
    # Final fallback: return the last meaningful part
    if len(path_parts) >= 2:
        return path_parts[-1].replace('-', '_')
    
    return None


def build_tab_mapping():
    """Recursively walk Django URL patterns and build the tab map."""
    from django.urls import get_resolver
    tab_mapping = {}
    _analyze_url_patterns(get_resolver().url_patterns, tab_mapping, "")

    # Merge declarative overrides
    declarative = _load_declarative_tabnames()
    tab_mapping.update(declarative)
    return tab_mapping

