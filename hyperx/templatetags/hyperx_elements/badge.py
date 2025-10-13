"""
    <hx:badge>
    ─────────────────────────────────────────────
    Declarative Bootstrap badge for status labels or counters.

    🧠 ATTRIBUTES
    • level="secondary|primary|success|warning|danger" → Color style.
    • text="..." → Badge content.
    • pill="true|false" → Rounded-pill variant.

    🧩 EXAMPLE
    {% hx %}
      <hx:badge level="success" pill="true">Active</hx:badge>
    {% endhx %}
"""



from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from django.utils.html import escape

_logger = load_logger("hx-badge")
_logger.info("hx-badge initialized")


@register_hx_tag("badge")
def convert_badge(tag, attrs):
    """
    Usage:
      <hx:badge level="success" text="Active" />
      <hx:badge level="warning">Pending</hx:badge>
    """
    level = attrs.get("level", "secondary")
    text = tag.decode_contents() or escape(attrs.get("text", "Badge"))
    pill = attrs.get("pill", "false").lower() in ("true", "1", "yes")

    pill_class = "rounded-pill" if pill else ""
    return f'<span class="badge bg-{level} {pill_class}">{text}</span>'
