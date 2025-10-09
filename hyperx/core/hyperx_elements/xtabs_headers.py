"""
hx:grid
────────────────────────────────────────────
Responsive card grid system.
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


def parse_xtab_header(request):
    """
    Parse X-Tab header into a structured dict
    
    Expected format: "tab:version:function:command"
    Example: "profile:1.0:load:view" -> {
        'tab': 'profile',
        'version': '1.0', 
        'function': 'load',
        'command': 'view',
        'raw': 'profile:1.0:load:view'
    }
    
    Returns:
        dict: Parsed X-Tab components or None if header missing
    """
    logger_htmx_impl.debug("Parsing X-Tab header from request")
    
    header = request.headers.get("X-Tab")
    if not header:
        logger_htmx_impl.debug("No X-Tab header found in request")
        return None

    logger_htmx_impl.debug(f"Found X-Tab header: {header}")
    
    parts = header.split(":")
    
    # Validate minimum required parts
    if len(parts) < 4:
        logger_htmx_validation.warning(f"Invalid X-Tab header format: {header} (expected 4 parts, got {len(parts)})")
        logger_htmx_security.warning(f"Malformed X-Tab header attempt: {header}, IP={request.META.get('REMOTE_ADDR')}")
        return None
    
    parsed_xtab = {
        "tab": parts[0] if parts[0] else None,
        "version": parts[1] if parts[1] else None,
        "function": parts[2] if parts[2] else None,
        "command": parts[3] if parts[3] else None,
        "raw": header,
        "parts_count": len(parts)
    }
    
    # Add any extra parts as additional data
    if len(parts) > 4:
        parsed_xtab["extra"] = parts[4:]
        logger_htmx_impl.debug(f"X-Tab header has {len(parts) - 4} extra parts: {parts[4:]}")
    
    logger_htmx_impl.info(f"X-Tab header parsed successfully: tab={parsed_xtab['tab']}, function={parsed_xtab['function']}, command={parsed_xtab['command']}")
    logger_htmx_performance.debug(f"X-Tab parsing: {len(parts)} parts processed")
    
    return parsed_xtab
