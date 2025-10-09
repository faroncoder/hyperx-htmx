from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


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