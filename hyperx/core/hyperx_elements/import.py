from hyperx.templatetags.hyperx import register_hx_tag
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
        html += f'<link type="text/css" rel="stylesheet" href="{static_func(f"css/{css}")}">\n'
    if js:
        html += f'<script type="text/javascript" src="{static_func(f"js/{js}")}"></script>\n'

    return html 


