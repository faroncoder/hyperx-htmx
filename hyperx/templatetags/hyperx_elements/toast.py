"""
    <hx:toast>
    ─────────────────────────────────────────────
    Declarative toast notification.

    🧠 ATTRIBUTES
    • message="Operation successful!"
    • level="success|info|warning|danger"
    • duration="4000" → Auto-dismiss in ms.

    🧩 EXAMPLE
    <hx:toast message="User saved!" level="success" duration="3000" />
    """


from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-toast")
_logger.info("hx-toast initialized")


@register_hx_tag("toast")
def convert_toast(tag, attrs):
    """
    Simple declarative notification:
    <hx:toast message="User saved!" level="success" duration="4000" />
    """
    message = attrs.get("message", "Operation successful!")
    level = attrs.get("level", "info")
    duration = int(attrs.get("duration", 4000))
    safe_msg = escape(message)

    return f"""
    <div class="toast align-items-center text-bg-{level} border-0 show fade" role="alert" id="toast-{level}">
      <div class="d-flex">
        <div class="toast-body">{safe_msg}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
    <script>
      setTimeout(() => {{
        const toast = document.getElementById("toast-{level}");
        if (toast) toast.remove();
      }}, {duration});
    </script>
    """