from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


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
