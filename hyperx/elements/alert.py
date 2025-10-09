"""
hx:alert
────────────────────────────────────────────
Declarative Bootstrap alert component.
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

@register_hx_tag("alert")
def convert_alert(tag, attrs):
    """
    Usage:
      <hx:alert level="danger" dismissible="true">Error occurred!</hx:alert>
    """
    level = attrs.get("level", "info")
    dismissible = attrs.get("dismissible", "true").lower() in ("true", "1", "yes")
    content = tag.decode_contents() or escape(attrs.get("message", "Alert!"))

    dismiss_html = ""
    if dismissible:
        dismiss_html = '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>'

    return f"""
    <div class="alert alert-{level} alert-dismissible fade show" role="alert">
      {content}
      {dismiss_html}
    </div>
    """
