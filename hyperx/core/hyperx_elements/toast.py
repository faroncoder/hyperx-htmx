from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


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