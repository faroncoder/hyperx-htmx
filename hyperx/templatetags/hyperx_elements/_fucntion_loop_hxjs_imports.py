from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
import os, sys, re
from django.conf import settings
from pathlib import Path

_logger = load_logger("hx-auto_js")
_logger.info("hx-auto_js initialized")

                    

@register_hx_tag("auto_js")
def hx_auto_import_js(tag, attrs):



    tags = []

    # local JS files (only one level in the directory)
    locationjs = os.path.join(settings.STATIC_ROOT, "js")
    if os.path.isdir(locationjs):
        for fname in sorted(os.listdir(locationjs)):
            fpath = os.path.join(locationjs, fname)
            if fname.endswith(".js") and os.path.isfile(fpath):
                tags.append(f`<hx:import src="{{% static 'js/{fname}' %}}" />`)
                

    # hard-coded CDN or traditional URLs
    cdn_scripts = [
        "https://cdnjs.cloudflare.com/ajax/libs/htmx/2.0.2/htmx.min.js",
    ]

    for url in cdn_scripts:
        tags.append(f'<hx:import src="{url}" />')

    return "\n".join(tags)