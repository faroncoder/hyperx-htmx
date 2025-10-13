from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-xtab")
_logger.info("hx-xtab initialized")





# ─────────────────────────────────────────────
# 🧩 X-Tab Header Parser
# ─────────────────────────────────────────────
def parse_xtab_header(request):
    """
    Parse X-Tab header into a structured dict.

    Expected format:
        "entity:type:opac:function:command[:extra...]"
    Example:
        "dashboard:panel:public:render:init:v1"
    Returns:
        dict or None
    """
    header = request.headers.get("X-Tab")
    if not header:
        logger.debug("No X-Tab header found in request")
        return None

    parts = header.split(":")
    base_keys = ["entity", "type", "opac", "function", "command"]

    if len(parts) < 5:
        logger.warning(f"Invalid X-Tab header format: {header}")
        return None

    parsed_xtab = dict(zip(base_keys, parts[:5]))
    parsed_xtab["raw"] = header
    parsed_xtab["parts_count"] = len(parts)

    if len(parts) > 5:
        parsed_xtab["extra"] = parts[5:]
        logger.debug(f"X-Tab header has {len(parts) - 5} extra parts: {parts[5:]}")

    logger.info(
        f"X-Tab header parsed: entity={parsed_xtab['entity']}, "
        f"function={parsed_xtab['function']}, command={parsed_xtab['command']}"
    )
    return parsed_xtab


# ─────────────────────────────────────────────
# 🧩 X-Tab Header Builder (future-proof)
# ─────────────────────────────────────────────
def build_xtab_header(attrs, *extra, **kwargs):
    """
    Build a forward-compatible X-Tab (CXVector-style) header.

    Standard fields:
        entity : type : opac : function : command

    Accepts arbitrary extras via *extra or kwargs['extras'],
    and an optional dict in kwargs['meta'] for JSON metadata.
    """
    parts = [
        attrs.get("entity", "unknown"),
        attrs.get("type", "component"),
        attrs.get("opac", "public"),
        attrs.get("function", "none"),
        attrs.get("command", "init"),
    ]

    # Positional extras
    if extra:
        parts.extend(str(e) for e in extra)

    # Keyword extras
    extras_kw = kwargs.get("extras")
    if extras_kw:
        if isinstance(extras_kw, (list, tuple)):
            parts.extend(str(x) for x in extras_kw)
        else:
            parts.append(str(extras_kw))

    # Optional meta dict
    meta = kwargs.get("meta")
    if isinstance(meta, dict):
        parts.append(json.dumps(meta, separators=(",", ":")))

    header_value = ":".join(parts)
    logger.debug(f"Built X-Tab header: {header_value}")
    return {"X-Tab": header_value}



@register_hx_tag("xtab")
def convert_xtab(tag, attrs):
    headers = {"X-Tab": f"{attrs.get('name')}:{attrs.get('version','1')}:{attrs.get('function')}:{attrs.get('command')}"}
    htmx = build_htmx_attrs(**attrs)
    htmx["hx-headers"] = json.dumps(headers)
    attrs = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs}></div>"
