"""
    <hx:field>
    ─────────────────────────────────────────────
    Declarative form field generator.

    🧠 ATTRIBUTES
    • label="Email" → Display label.
    • name="email" → Input name.
    • type="text|email|number" → Input type.
    • required="true|false"
    • help="..." → Helper text.

    🧩 EXAMPLE
    <hx:field label="Email" name="email" type="email" help="We never share it." />
    """

from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-field")
_logger.info("hx-field initialized")

@register_hx_tag("field")
def convert_field(tag, attrs):
    """
    Generic field generator.

    <hx:field label="Email" name="email" type="email" required="true" help="We'll never share it." />
    """
    label = attrs.get("label", "")
    name = attrs.get("name", "")
    ftype = attrs.get("type", "text")
    required = "required" if attrs.get("required") in ("true", "1", True) else ""
    helptext = attrs.get("help", "")
    placeholder = attrs.get("placeholder", label)

    return f"""
    <div class="mb-3">
      <label for="id_{name}" class="form-label">{label}</label>
      <input type="{ftype}" name="{name}" id="id_{name}"
             class="form-control" placeholder="{placeholder}" {required}>
      {f'<div class="form-text">{helptext}</div>' if helptext else ''}
    </div>
    """