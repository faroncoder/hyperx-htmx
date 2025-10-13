from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-form")

_logger.info("hx-form initialized")


@register_hx_tag("form")
def convert_form(tag, attrs):
    """
    Simplified form builder:
    <hx:form post="user:save" target="#main" indicator="#loader" confirm="Save user?" />
    """
    action = attrs.get("post") or attrs.get("get", "")
    method = "post" if "post" in attrs else "get"
    target = attrs.get("target", "#main")
    indicator = attrs.get("indicator", "")
    confirm = attrs.get("confirm", "")
    swap = attrs.get("swap", "innerHTML")

    confirm_attr = f'hx-confirm="{escape(confirm)}"' if confirm else ""
    indicator_attr = f'hx-indicator="{indicator}"' if indicator else ""

    return f"""
    <form hx-{method}="{action}" hx-target="{target}" hx-swap="{swap}" {confirm_attr} {indicator_attr}>
      {tag.decode_contents()}
    </form>
    """