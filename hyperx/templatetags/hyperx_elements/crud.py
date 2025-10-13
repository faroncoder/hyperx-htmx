"""
    <hx:crud>
    ─────────────────────────────────────────────
    Declarative CRUD container that auto-wires forms, tables, and pagination.

    🧠 ATTRIBUTES
    • model="User" → Target model name.
    • endpoint="users" → API endpoint.
    • target="#zone" → Rendering target.

    🧩 EXAMPLE
    {% hx %}
      <hx:crud model="User" endpoint="users" target="#crud-zone">
        <hx:form ... />
        <hx:table ... />
      </hx:crud>
    {% endhx %}
    """


from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-crud")
_logger.info("hx-crud initialized")

@register_hx_tag("crud")
def convert_crud(tag, attrs):
    """
    Declarative CRUD container that auto-wires form + table + pagination.
    Example:
      <hx:crud model="User" endpoint="users" target="#crud-zone">
        <hx:form ... />
        <hx:table ... />
      </hx:crud>
    """
    model_name = attrs.get("model")
    endpoint = attrs.get("endpoint")
    target = attrs.get("target", "#content")

    inner_html = tag.decode_contents()
    base = f"""
    <div id="{target.strip('#')}" class="hx-crud"
         data-model="{model_name}" data-endpoint="{endpoint}">
      {inner_html}
    </div>
    """
    return base
