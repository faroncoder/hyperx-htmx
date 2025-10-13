"""
    <hx:alert>
    ─────────────────────────────────────────────
    Declarative Bootstrap alert component for messages and system notices.

    ✅ PURPOSE
    Provides a styled alert box that can be dismissible and dynamically injected.

    🧠 ATTRIBUTES
    • level="info|success|warning|danger" → Alert color scheme.
    • dismissible="true|false" → Enables a close button.
    • message="..." or inner content → Sets alert text.

    🧩 EXAMPLE
    {% hx %}
      <hx:alert level="danger" dismissible="true">An error occurred!</hx:alert>
    {% endhx %}
    """


from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from django.utils.html import escape
_logger = load_logger("hx-alert")
_logger.info("hx-alert initialized")



@register_hx_tag("alert")
def convert_alert(tag, attrs):
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
