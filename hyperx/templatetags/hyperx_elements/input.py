"""
    <hx:input>
    ─────────────────────────────────────────────
    Standalone input field builder.

    🧠 ATTRIBUTES
    • name="username"
    • type="text|email|password"
    • placeholder="Enter username"

    🧩 EXAMPLE
    <hx:input name="username" placeholder="Enter username" />
    """
from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-input")
_logger.info("hx-input initialized")

@register_hx_tag("input")
def convert_input(tag, attrs):
    """
    Quick standalone input.

    <hx:input name="username" placeholder="Enter username" />
    """
    name = attrs.get("name", "")
    placeholder = attrs.get("placeholder", "")
    value = attrs.get("value", "")
    itype = attrs.get("type", "text")

    return f'<input type="{itype}" name="{name}" value="{value}" class="form-control" placeholder="{placeholder}">'
