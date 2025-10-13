"""
    <hx:select>
    ─────────────────────────────────────────────
    Declarative dropdown menu builder.

    🧠 ATTRIBUTES
    • label="Role"
    • name="role"
    • options="Student,Teacher,Admin"

    🧩 EXAMPLE
    <hx:select label="Role" name="role" options="Student,Teacher,Admin" />
    """

from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-select")
_logger.info("hx-select initialized")


@register_hx_tag("select")
def convert_select(tag, attrs):

    label = attrs.get("label", "")
    name = attrs.get("name", "")
    options = attrs.get("options", "")
    choices = [o.strip() for o in options.split(",") if o.strip()]

    opts_html = "".join(f'<option value="{escape(o)}">{escape(o)}</option>' for o in choices)

    return f"""
    <div class="mb-3">
      <label for="id_{name}" class="form-label">{label}</label>
      <select name="{name}" id="id_{name}" class="form-select">
        {opts_html}
      </select>
    </div>
    """