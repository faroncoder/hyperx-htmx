"""
    <hx:grid>
    ─────────────────────────────────────────────
    Responsive card grid layout wrapper.

    🧠 ATTRIBUTES
    • cols="3" → Number of columns.
    • gap="2|3|4" → Bootstrap gap spacing.

    🧩 EXAMPLE
    <hx:grid cols="3" gap="3">
      <div class="card">Item 1</div>
      <div class="card">Item 2</div>
    </hx:grid>
"""

from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-grid")
_logger.info("hx-grid initialized") 



@register_hx_tag("grid")
def convert_grid(tag, attrs):

    cols = int(attrs.get("cols", 3))
    gap = attrs.get("gap", "3")
    inner_html = tag.decode_contents() or "<!-- grid items -->"
    return f'<div class="row row-cols-{cols} g-{gap}">{inner_html}</div>'
