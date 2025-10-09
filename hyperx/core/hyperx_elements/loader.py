"""
hx:loader
────────────────────────────────────────────
Declarative loading indicator (inline or global overlay).
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

@register_hx_tag("loader")
def convert_loader(tag, attrs):
    """
    Usage:
      <hx:loader id="global-loader" text="Loading..." fullscreen="true" />
    """
    loader_id = attrs.get("id", "hx-loader")
    text = escape(attrs.get("text", "Loading..."))
    fullscreen = attrs.get("fullscreen", "false").lower() in ("true", "1", "yes")

    if fullscreen:
        return f"""
        <div id="{loader_id}" class="hx-loader-overlay" style="display:none;
             position:fixed;top:0;left:0;width:100%;height:100%;
             background:rgba(0,0,0,0.5);z-index:1050;align-items:center;justify-content:center;">
          <div class="spinner-border text-light" role="status"></div>
          <span class="ms-2 text-light">{text}</span>
        </div>
        <script>
        document.addEventListener("htmx:beforeRequest", () => document.getElementById("{loader_id}").style.display = "flex");
        document.addEventListener("htmx:afterOnLoad", () => document.getElementById("{loader_id}").style.display = "none");
        document.addEventListener("htmx:responseError", () => document.getElementById("{loader_id}").style.display = "none");
        </script>
        """
    else:
        return f"""
        <div id="{loader_id}" class="text-center py-3" style="display:none;">
          <div class="spinner-border text-primary" role="status"></div>
          <span class="ms-2">{text}</span>
        </div>
        <script>
        document.addEventListener("htmx:beforeRequest", () => document.getElementById("{loader_id}").style.display = "block");
        document.addEventListener("htmx:afterOnLoad", () => document.getElementById("{loader_id}").style.display = "none");
        </script>
        """
