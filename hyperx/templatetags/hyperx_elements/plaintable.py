from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-plaintable")
_logger.info("hx-plaintable initialized")



@register_hx_tag("plaintable")
def convert_plaintable(tag, attrs):
    """
    Render a plain Bootstrap-style table with no CRUD logic.
    Example:
      <hx:plaintable fields="id,username,email" data-target="#users-table" />
    """
    fields = [f.strip() for f in attrs.get("fields", "").split(",") if f.strip()]
    table_class = attrs.get("class", "table table-striped table-hover align-middle")
    caption = attrs.get("caption", "")

    # Build header
    header_html = "".join(f"<th>{f.title()}</th>" for f in fields)

    html = f"""
    <table class="{table_class}">
        {"<caption>" + caption + "</caption>" if caption else ""}
        <thead><tr>{header_html}</tr></thead>
        <tbody>
            <tr><td colspan="{len(fields)}" class="text-center text-muted py-3">
                <i class="fas fa-info-circle me-2"></i>No data available.
            </td></tr>
        </tbody>
    </table>
    """
    return html