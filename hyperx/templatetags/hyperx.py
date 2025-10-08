"""
hyperx/templatetags/hyperx.py
────────────────────────────────────────────
Declarative <hx:*> template tag system with compiler integration.
"""

from django import template
from django.utils.safestring import mark_safe
from bs4 import BeautifulSoup
from hyperx.compiler import HyperXCompiler
from hyperx.core import build_htmx_attrs
import json

register = template.Library()

# ─────────────────────────────────────────────
# 🔧 Tag Converter Registry
# ─────────────────────────────────────────────
TAG_CONVERTERS = {}

def register_hx_tag(tag_name):
    """Decorator for registering new <hx:*> tag converters."""
    def wrapper(func):
        TAG_CONVERTERS[tag_name] = func
        return func
    return wrapper


# ─────────────────────────────────────────────
# 🧠 Basic converters (panel, button, xtab)
# ─────────────────────────────────────────────
@register_hx_tag("panel")
def convert_panel(tag, attrs):
    htmx = build_htmx_attrs(**attrs)
    attrs = ' '.join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs}></div>"

@register_hx_tag("button")
def convert_button(tag, attrs):
    label = attrs.get("label", "Action")
    htmx = build_htmx_attrs(**attrs)
    attrs = ' '.join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<button {attrs}>{label}</button>"

@register_hx_tag("xtab")
def convert_xtab(tag, attrs):
    headers = {"X-Tab": f"{attrs.get('name')}:{attrs.get('version','1')}:{attrs.get('function')}:{attrs.get('command')}"}
    htmx = build_htmx_attrs(**attrs)
    htmx["hx-headers"] = json.dumps(headers)
    attrs = ' '.join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs}></div>"

def convert_generic(tag, attrs):
    htmx = build_htmx_attrs(**attrs)
    attrs_str = ' '.join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs_str}></div>"



@register_hx_tag("meta")
def convert_meta(tag, attrs):
    """
    Declaratively inject <title>, <meta>, or <script type="application/json"> tags.
    """
    tag_type = attrs.get("type", "meta")
    title = attrs.get("title")
    description = attrs.get("description")
    name = attrs.get("name")
    content = attrs.get("content")
    data = attrs.get("data")
    element_id = attrs.get("id")

    fragments = []

    # <title> support
    if title:
        fragments.append(f"<title>{title}</title>")
    if description:
        fragments.append(f'<meta name="description" content="{description}">')

    # <meta name="..." content="...">
    if name and content:
        fragments.append(f'<meta name="{name}" content="{content}">')

    # <script type="application/json"> injection
    if tag_type.lower() == "json" and data:
        fragments.append(
            f'<script id="{element_id or "hx-data"}" type="application/json">{data}</script>'
        )

    return "\n".join(fragments)







# ─────────────────────────────────────────────
# 🔨 Tag processor & AST compiler integration
# ─────────────────────────────────────────────
@register.tag(name="hx")
def do_hx(parser, token):
    """
    Usage:
        {% hx [debug=True] %}
            <hx:panel get="lti:admin:course_table_view" target="#intel-container">
                <hx:button post="lti:teacher:sync_grades" label="Sync Grades" />
            </hx:panel>
        {% endhx %}
    """
    bits = token.split_contents()
    debug = "debug=True" in bits
    nodelist = parser.parse(("endhx",))
    parser.delete_first_token()
    return HXNode(nodelist, debug)


class HXNode(template.Node):
    def __init__(self, nodelist, debug=False):
        self.nodelist = nodelist
        self.debug = debug

    def render(self, context):
        rendered = self.nodelist.render(context)

        # ✅ Run through HyperXCompiler
        compiler = HyperXCompiler(rendered)
        ast_root = compiler.parse()

        if self.debug:
            print("\n[HyperX Compiler] Parsed nodes:")
            print(ast_root)

        # ✅ Render to HTMX HTML using converter registry
        soup = BeautifulSoup(rendered, "html.parser")
        for tag in soup.find_all(lambda t: t.name and t.name.startswith("hx:")):
            tag_type = tag.name.split(":")[1]
            attrs = dict(tag.attrs)
            converter = TAG_CONVERTERS.get(tag_type, convert_generic)
            html = converter(tag, attrs)
            tag.replace_with(BeautifulSoup(html, "html.parser"))

        final_html = str(soup)

        if self.debug:
            print("[HyperX Rendered HTML]")
            print(final_html)

        return mark_safe(final_html)



@register_hx_tag("include")
def convert_include(tag, attrs):
    """
    Dynamically include another template file declaratively:
      <hx:include file="path/to/template.html" context="{'key': 'value'}" />
    """
    from django.template.loader import render_to_string

    file_path = attrs.get("file")
    if not file_path:
        return "<!-- Missing file attribute in <hx:include> -->"

    # Optional context (JSON/dict string)
    ctx_str = attrs.get("context", "{}")
    try:
        local_ctx = json.loads(ctx_str.replace("'", '"')) if ctx_str else {}
    except Exception:
        local_ctx = {}

    try:
        rendered = render_to_string(file_path, local_ctx)
        return rendered
    except Exception as e:
        return f"<!-- Failed to include {file_path}: {e} -->"




@register_hx_tag("import")
def convert_import(tag, attrs):
    """
    Declaratively import CSS or JS assets.
    Example:
      <hx:import css="css/style.css" js="js/app.js" />
    """
    css_links, js_scripts = [], []

    # CSS imports
    for css_file in attrs.get("css", "").split(","):
        css_file = css_file.strip()
        if css_file:
            css_links.append(f'<link rel="stylesheet" href="{css_file}">')

    # JS imports
    for js_file in attrs.get("js", "").split(","):
        js_file = js_file.strip()
        if js_file:
            js_scripts.append(f'<script src="{js_file}"></script>')

    # Optional inline script
    inline = attrs.get("inline")
    if inline:
        js_scripts.append(f"<script>{inline}</script>")

    return "\n".join(css_links + js_scripts)

