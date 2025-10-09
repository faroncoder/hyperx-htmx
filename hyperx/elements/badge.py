"""
hx:badge
────────────────────────────────────────────
Compact label for statuses, roles, or counts.
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

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
