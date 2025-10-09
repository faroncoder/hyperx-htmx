from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

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