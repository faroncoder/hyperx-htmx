"""
    <hx:pagination>
    ─────────────────────────────────────────────
    Declarative pagination component.

    🧠 ATTRIBUTES
    • source="users:list" → URL or view to fetch.
    • current="1" → Current page.
    • total="10" → Total pages.
    • target="#table" → Where to inject.

    🧩 EXAMPLE
    <hx:pagination source="users:list" current="3" total="12" target="#table" />
    """



from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape

_logger = load_logger("hx-button")
_logger.info("hx-button initialized")


@register_hx_tag("button")
def convert_button(tag, attrs):
    label = attrs.get("label", "Action")
    htmx = build_htmx_attrs(**attrs)
    attrs = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<button {attrs}>{label}</button>"