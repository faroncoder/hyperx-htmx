"""
hx:grid
────────────────────────────────────────────
Responsive card grid system.
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

@register_hx_tag("grid")
def convert_grid(tag, attrs):
    """
    Usage:
      <hx:grid cols="3" gap="3">
        <div class="card">Item 1</div>
        <div class="card">Item 2</div>
      </hx:grid>
    """
    cols = int(attrs.get("cols", 3))
    gap = attrs.get("gap", "3")
    inner_html = tag.decode_contents() or "<!-- grid items -->"
    return f'<div class="row row-cols-{cols} g-{gap}">{inner_html}</div>'
