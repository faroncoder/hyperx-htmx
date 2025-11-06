"""
Enhanced HTMX Attributes Builder
"""
import json
from django.urls import reverse
from django.conf import settings
from django.urls import reverse



# 🔐 Optional: environment-aware prefix for consistency across all utils
PREFIX = getattr(settings, "HTMX_CACHE_PREFIX", "hyperx:htmx:")



def build_htmx_attrs(get=None, post=None, put=None, delete=None,
                     target=None, swap=None, trigger=None,
                     headers=None, push_url=None, vals=None, params=None,
                     xtab=None, confirm=None):
    """
    Build a dict of htmx-compatible attributes.
    
    xtab = (tab_name, function, command, version)
    Produces X-Tab header like "tab:version:function:command"
    
    Returns dict: {'hx-get': '/url/', 'hx-target': '#selector', ...}
    """
    attrs = {}

    # Map standard HX verbs with URL reversal
    try:
        if get:
            url = reverse(get) if ":" in str(get) else get
            attrs["hx-get"] = url
        if post:
            url = reverse(post) if ":" in str(post) else post
            attrs["hx-post"] = url
        if put:
            url = reverse(put) if ":" in str(put) else put
            attrs["hx-put"] = url
        if delete:
            url = reverse(delete) if ":" in str(delete) else delete
            attrs["hx-delete"] = url
    except Exception:
        # Fallback if reverse fails
        if get:
            attrs["hx-get"] = str(get)
        if post:
            attrs["hx-post"] = str(post)
        if put:
            attrs["hx-put"] = str(put)
        if delete:
            attrs["hx-delete"] = str(delete)

    # HTMX modifiers
    if target:
        attrs["hx-target"] = target
    if swap:
        attrs["hx-swap"] = swap
    if trigger:
        attrs["hx-trigger"] = trigger
    if confirm:
        attrs["hx-confirm"] = confirm
    if push_url is not None:
        attrs["hx-push-url"] = str(push_url).lower()
    if vals:
        val_str = json.dumps(vals) if isinstance(vals, dict) else str(vals)
        attrs["hx-vals"] = val_str
    if params:
        attrs["hx-params"] = str(params)

    # X-Tab headers
    if xtab:
        tab_name, function, command, version = xtab
        xtab_header = f"{tab_name}:{version}:{function}:{command}"
        if headers:
            headers_dict = json.loads(headers) if isinstance(headers, str) else headers
            headers_dict["X-Tab"] = xtab_header
        else:
            headers_dict = {"X-Tab": xtab_header}
        attrs["hx-headers"] = json.dumps(headers_dict)
    elif headers:
        header_str = json.dumps(headers) if isinstance(headers, dict) else str(headers)
        attrs["hx-headers"] = header_str

    return attrs

def attrs_to_string(attrs):
    """
    Convert attributes dict to HTML string
    """
    return " ".join([f'{key}="{value}"' for key, value in attrs.items()])

def attrs_to_dict(attrs):
    """
    Convert attributes dict to dictionary (identity function)
    """
    return dict(attrs)