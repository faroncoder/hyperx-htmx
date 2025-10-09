from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


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
