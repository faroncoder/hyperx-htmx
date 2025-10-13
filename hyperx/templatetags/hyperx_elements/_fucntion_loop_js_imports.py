from django import template
register = template.Library()
from hyperx.templatetags.hyperx import register_hx_tag, build_htmx_attrs
from django.utils.html import escape
import json
from django.conf import settings
from django.templatetags.static import static
import os
from pathlib import Path
import json

@register_hx_tag("auto_js")
def hx_auto_import_js(tag, attrs):

    # Find BASE_DIR by walking up until manage.py is found
    current_dir = Path(__file__).resolve().parent
    while True:
        if (current_dir / "manage.py").exists():
            BASE_DIR = str(current_dir)
            break
        if current_dir.parent == current_dir:
            raise FileNotFoundError("manage.py not found in any parent directory.")
        current_dir = current_dir.parent

    static_js = os.path.join(BASE_DIR, "static", "js")
    if os.path.isdir(static_js):
        for filename in sorted(os.listdir(static_js)):
            if filename.endswith(".js"):
                # Use double quotes for f-string, and Django template syntax should be inside the string
                jstags.append(f'<hx:import src="{{% static \'js/{filename}\' %}}" />')


    return "\n".join(jstags)