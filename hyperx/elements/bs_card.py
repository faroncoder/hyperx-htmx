from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.logger.hx_logger import *
from hyperx.hx.hx_converter import register_hx_tag
from hyperx.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx_bootstrap_card")
_logger.info("hx-bootstrap-card initialized")



@register_hx_tag("bs_card")
def convert_bs_card(tag, attrs):
    title   = escape(attrs.get("title", "Card Title"))
    footer  = escape(attrs.get("footer", ""))
    color   = attrs.get("color", "light")  # e.g. bg-light, bg-dark
    border  = attrs.get("border", "0")
    shadow  = attrs.get("shadow", "shadow-sm")
    body    = tag.decode_contents() or "<!-- card body -->"

    # Build card HTML
    header_html = f'<div class="card-header bg-{color} text-dark"><h5 class="mb-0">{title}</h5></div>'
    body_html   = f'<div class="card-body">{body}</div>'
    footer_html = f'<div class="card-footer bg-{color} text-muted">{footer}</div>' if footer else ""

    return f"""
    <div class="card border-{border} {shadow} mb-3">
      {header_html}
      {body_html}
      {footer_html}
    </div>
    """