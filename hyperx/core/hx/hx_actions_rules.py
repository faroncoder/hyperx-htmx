"""
HyperX core tag utilities
──────────────────────────────
Defines:
    - register_hx_tag() : decorator for tag converters
    - build_htmx_attrs() : builds HTMX attributes for Django templates
"""

from django import template
from django.urls import reverse
from django.utils.html import escape
from hyperx.bin.cli.logger.hx_logger import load_logger
import json
import logging

register = template.Library()
_logger = load_logger("hx_elements_core")
_logger.info("hx_elements core initialized")



# ─────────────────────────────────────────────
# Attribute Builder
# ─────────────────────────────────────────────
def build_htmx_attrs(
    request=None,
    get=None,
    post=None,
    put=None,
    delete=None,
    target=None,
    swap=None,
    trigger=None,
    headers=None,
    push_url=None,
    vals=None,
    params=None,
    xtab=None,
    **kwargs
):
    """Build a list of HTMX-style attributes for rendering."""
    attrs = []

    # Legacy call compatibility
    if request is not None and isinstance(request, str):
        get = request
        request = None
        _logger.debug("Legacy parameter style detected: first param treated as 'get' URL")

    # Helper for resolving URL names safely
    def _resolve_url(value):
        try:
            if ":" in str(value):
                return reverse(value)
            return value
        except Exception:
            return value

    # Explicit HTTP method attributes
    for method_name, val in {"get": get, "post": post, "put": put, "delete": delete}.items():
        if val:
            url = _resolve_url(val)
            attrs.append({"name": f"hx-{method_name}", "value": url})
            _logger.debug(f"{method_name.upper()} mapped: {val} -> {url}")

    # Other direct parameters
    if target:
        attrs.append({"name": "hx-target", "value": target})
    if swap:
        attrs.append({"name": "hx-swap", "value": swap})
    if trigger:
        attrs.append({"name": "hx-trigger", "value": trigger})
    if headers:
        headers_value = json.dumps(headers) if isinstance(headers, dict) else str(headers)
        attrs.append({"name": "hx-headers", "value": headers_value})
    if push_url is not None:
        attrs.append({"name": "hx-push-url", "value": str(push_url).lower()})
    if vals:
        attrs.append({"name": "hx-vals", "value": vals})
    if params:
        attrs.append({"name": "hx-params", "value": params})

    # Handle X-Tab header (tuple or dict)
    if xtab:
        if isinstance(xtab, (list, tuple)) and len(xtab) >= 4:
            tab_name, type_, version, command = xtab[:4]
            x_tab_value = f"{tab_name}:{type_}:{version}:{command}"
        elif isinstance(xtab, dict):
            x_tab_value = ":".join(str(xtab.get(k, "unknown")) for k in ["tab", "type", "version", "command"])
        else:
            x_tab_value = str(xtab)

        x_tab_header = json.dumps({"X-Tab": x_tab_value})
        attrs.append({"name": "hx-headers", "value": x_tab_header})
        _logger.debug(f"X-Tab header added: {x_tab_value}")

    # Additional kwargs → hx-kebab-case
    for key, value in kwargs.items():
        if key.startswith("on_"):
            event = key.replace("on_", "")
            attr_name = f"hx-on:{event}"
        else:
            attr_name = f"hx-{key.replace('_', '-')}"
        attrs.append({"name": attr_name, "value": value})
        _logger.debug(f"Mapped extra attribute: {key} -> {attr_name}")

    _logger.info(f"HTMX attributes built successfully: {len(attrs)} total attributes")
    return attrs
