from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


@register_hx_tag("select")
def convert_select(tag, attrs):
    """
    Declarative dropdown.

    <hx:select label="Role" name="role" options="Student,Teacher,Admin" />
    """
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