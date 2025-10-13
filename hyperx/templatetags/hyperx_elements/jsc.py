from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-jsc")
_logger.info("hx-jsc initialized")

from django.conf import settings
import os, tempfile
from pathlib import Path
import hashlib




@register_hx_tag("css_file")
def convert_css_file(tag, attrs):
    """
    Render external CSS <link> tags for provided CSS files.

    Examples:
        <hx:css_file css="css/main.css, css/vendor/bootstrap.css" />
        <hx:css_file css="css/main.css" />
    """
    css_links = []
    css_attr = attrs.get("css", "")
    if css_attr:
        for css_file in css_attr.split(","):
            css_file = css_file.strip()
            if css_file:
                css_links.append(f'<link type="text/css" rel="stylesheet" href="{{% static \'{css_file}\' %}}">')
    return "\n".join(css_links) if css_links else "<!-- no CSS provided -->"


@register_hx_tag("css_inline")
def convert_css_inline(tag, attrs):
    """
    Convert inline CSS into a file under STATIC_ROOT/css and
    return a <link rel="stylesheet" href="{% static 'css/filename.css' %}"> tag.

    Examples:
        <hx:css_inline inline="body { background: #fff; }" />
        <hx:css_inline inline=".foo { color: red; }" />
    """
    css_content = attrs.get("inline")
    if not css_content:
        return "<!-- No inline CSS provided -->"

    # Join lists or tuples into one string
    if isinstance(css_content, (list, tuple)):
        css_text = "\n".join(css_content)
    else:
        css_text = str(css_content)

    # Build hashed filename for caching / deduplication
    digest = hashlib.sha1(css_text.encode("utf-8")).hexdigest()[:10]
    css_dir = Path(getattr(settings, "STATIC_ROOT", Path.cwd())) / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    css_filename = f"inline_{digest}.css"
    css_path = css_dir / css_filename

    # Write file only if it doesn't already exist
    if not css_path.exists():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".css", mode="w", encoding="utf-8") as tmp:
            tmp.write(css_text)
            tmp_path = Path(tmp.name)
        tmp_path.replace(css_path)

    # Return Django static link
    return f'<link type="text/css" rel="stylesheet" href="{{% static \'css/{css_filename}\' %}}">'


@register_hx_tag("js_file")
def convert_js_file(tag, attrs):
    """
    Render external JS <script> tags first, then append inline JS.
    If 'inline' is provided, it can be written out as its own static file
    so it joins the group of JS assets.

    Examples:
        <hx:js_file js="js/main.js, js/vendor/jquery.js" />
        <hx:js_file js="js/main.js" inline="console.log('ready');" />
        <hx:js_file inline="alert('hi');" export="true" />
    """
    from django.conf import settings
    import tempfile, os, hashlib
    from pathlib import Path

    js_tags = []
    js_attr = attrs.get("js", "")
    inline_code = attrs.get("inline")

    # ─────────────────────────────────────────────
    # 1️⃣  External scripts first
    # ─────────────────────────────────────────────
    if js_attr:
        for js_file in js_attr.split(","):
            js_file = js_file.strip()
            if js_file:
                js_tags.append(f'<script src="{{% static \'{js_file}\' %}}"></script>')

    # ─────────────────────────────────────────────
    # 2️⃣  Inline code next (either inline or exported)
    # ─────────────────────────────────────────────
    if inline_code:
        export_inline = attrs.get("export") in ("1", "True", "yes")

        if export_inline:
            # write inline script as a .js file in STATIC_ROOT/js
            js_dir = Path(getattr(settings, "STATIC_ROOT", Path.cwd())) / "js"
            js_dir.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha1(inline_code.encode("utf-8")).hexdigest()[:10]
            filename = f"inline_{digest}.js"
            path = js_dir / filename

            if not path.exists():
                with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8") as tmp:
                    tmp.write(inline_code)
                    tmp_path = Path(tmp.name)
                tmp_path.replace(path)

            js_tags.append(f'<script src="{{% static \'js/{filename}\' %}}"></script>')
    else:
        js_tags.append(f"<script>\n{inline_code}\n</script>")

    return "\n".join(js_tags) + "\n" if js_tags else "<!-- no JS provided -->"


