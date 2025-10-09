from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape



@register_hx_tag("form")
def convert_form(tag, attrs):
    """
    Declarative form component.
    Example:
    <hx:form post="users:create" target="#main" toast="User created!" />
    """
    post = attrs.get("post")
    target = attrs.get("target", "#main")
    confirm = attrs.get("confirm", "")
    toast = attrs.get("toast", "")
    indicator = attrs.get("indicator", "")
    swap = attrs.get("swap", "innerHTML")

    confirm_attr = f'hx-confirm="{escape(confirm)}"' if confirm else ""
    indicator_attr = f'hx-indicator="{indicator}"' if indicator else ""

    toast_script = ""
    if toast:
        toast_script = f"""
        <script>
        document.body.addEventListener("htmx:afterOnLoad", function(e) {{
            const toast = document.createElement("div");
            toast.className = "toast align-items-center text-bg-success border-0 show fade";
            toast.innerHTML = `<div class='toast-body'>{escape(toast)}</div>`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }});
        </script>
        """

    # Render the form’s inner content (fields, buttons, etc.)
    inner_html = tag.decode_contents() or "<!-- form fields go here -->"

    return f"""
    <form hx-post="{post}" hx-target="{target}" hx-swap="{swap}" {confirm_attr} {indicator_attr}>
      <input type="hidden" name="csrfmiddlewaretoken" value="{{{{ csrf_token }}}}">
      {inner_html}
    </form>
    {toast_script}
    """
