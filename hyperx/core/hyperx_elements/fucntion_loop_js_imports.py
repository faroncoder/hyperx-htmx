from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

import json

                    

@register_hx_tag("auto_js")
def hx_auto_import_js(tag, attrs):

    from django.conf import settings
    from django.templatetags.static import static
    import os

    tags = []

    # local JS files
    locationjs = os.path.join(settings.STATIC_ROOT, "js")
    if os.path.isdir(locationjs):
        for fname in sorted(os.listdir(locationjs)):
            if fname.endswith(".js"):
                tags.append(f'<hx:import src="{static_func(f"js/{fname}")}" />')

    # hard-coded CDN or traditional URLs
    cdn_scripts = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/htmx/2.0.2/htmx.min.js",
    ]

    for url in cdn_scripts:
        tags.append(f'<hx:import src="{url}" />')

    return "\n".join(tags)