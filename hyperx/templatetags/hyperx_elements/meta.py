from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-meta")
_logger.info("hx-meta initialized")




@register_hx_tag("meta")
def convert_meta(tag, attrs):
    tag_type = attrs.get("type", "meta")
    title, description = attrs.get("title"), attrs.get("description")
    name, content, data = attrs.get("name"), attrs.get("content"), attrs.get("data")
    element_id = attrs.get("id")
    frags = []
    if title: frags.append(f"<title>{title}</title>")
    if description: frags.append(f'<meta name="description" content="{description}">')
    if name and content: frags.append(f'<meta name="{name}" content="{content}">')
    if tag_type.lower() == "json" and data:
        frags.append(f'<script id="{element_id or "hx-data"}" type="application/json">{data}</script>')
    return "\n".join(frags)
