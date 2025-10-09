# hyperx/context_processors.py
from django.templatetags.static import static
from django.conf import settings
from django.utils.safestring import mark_safe

def hyperx_runtime(request):
    """
    Inject HyperX runtime helper scripts automatically.
    Adds {{ HYPERX_RUNTIME_SCRIPTS }} to template context.
    """
    if not getattr(settings, "DEBUG", False):
        return {"HYPERX_RUNTIME_SCRIPTS": ""}

    scripts = [
        static("hxjs/loader.js"),
        static("hxjs/dragdrop.js"),
        static("hxjs/drawer.js"),
    ]
    html = "\n".join(f'<script type="module" src='{% script "{src}" %}'></script>' for src in scripts)
    return {"HYPERX_RUNTIME_SCRIPTS": mark_safe(html)}
