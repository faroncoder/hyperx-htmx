from django import template
register = template.Library()
from hyperx.templatetags.hyperx import register_hx_tag, build_htmx_attrs
from django.utils.html import escape

# ─────────────────────────────────────────────────────────────
# 4️⃣  Import Assets (CSS/JS)
# ─────────────────────────────────────────────────────────────
@register_hx_tag("import")
def convert_import(tag, attrs):
    """
    Import CSS/JS dynamically via HyperX:
    <hx:import css="css/admin.css" js="js/dashboard.js" />
    """
    css = attrs.get("css", "")
    js = attrs.get("js", "")
    html = ""

    if css:
        html += f'<link rel="stylesheet" href="/static/{css}">\n'
    if js:
        html += f'<script src="/static/{js}"></script>\n'

    return html 