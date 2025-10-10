from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

import json

@register_hx_tag("auto_css")
def hx_auto_import_css(tag, attrs):     
    from django.conf import settings
    from django.templatetags.static import static   
    import os 

    tags = []

    # local CSS files
    locationcss = os.path.join(settings.STATIC_ROOT, "css")
    if os.path.isdir(locationcss):
        for fname in sorted(os.listdir(locationcss)):
            if fname.endswith(".css"):
                tags.append(f'<hx:import src="{static_func(f"css/{fname}")}" />')

    return "\n".join(tags)
                    
                    