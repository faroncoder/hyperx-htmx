"""
hyperx/templatetags/hyperx.py
────────────────────────────────────────────
Declarative <hx:*> template tag system with compiler integration.
Auto-includes Bootstrap, static, and runtime helpers.
"""

import importlib, pkgutil, logging, json
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.library import import_library
from django.templatetags.static import static as static_func
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from ..core.compiler import HyperXCompiler
from ..core.core import build_htmx_attrs

_logger = logging.getLogger("hyperx")
register = template.Library()

# ─────────────────────────────────────────────
#  Django built-ins
# ─────────────────────────────────────────────
@register.simple_tag
def static(path):
    return static_func(path)

try:
    bootstrap_lib = import_library("bootstrap5")
except Exception:
    try:
        bootstrap_lib = import_library("django_bootstrap5")
    except Exception:
        bootstrap_lib = None

if bootstrap_lib:
    for n, t in bootstrap_lib.tags.items():
        register.tag(n, t)
    for n, f in bootstrap_lib.filters.items():
        register.filter(n, f)
    _logger.info("[HyperX] Bootstrap5 tags merged")
else:
    _logger.warning("[HyperX] Bootstrap5 not found")

# ─────────────────────────────────────────────
#  Tag converter registry
# ─────────────────────────────────────────────
TAG_CONVERTERS = {}

def register_hx_tag(tag_name):
    def wrapper(func):
        TAG_CONVERTERS[tag_name] = func
        return func
    return wrapper

# ─────────────────────────────────────────────
#  Basic converters
# ─────────────────────────────────────────────
@register_hx_tag("panel")
def convert_panel(tag, attrs):
    htmx = build_htmx_attrs(**attrs)
    attrs = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs}></div>"

@register_hx_tag("button")
def convert_button(tag, attrs):
    label = attrs.get("label", "Action")
    htmx = build_htmx_attrs(**attrs)
    attrs = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<button {attrs}>{label}</button>"

@register_hx_tag("xtab")
def convert_xtab(tag, attrs):
    headers = {"X-Tab": f"{attrs.get('name')}:{attrs.get('version','1')}:{attrs.get('function')}:{attrs.get('command')}"}
    htmx = build_htmx_attrs(**attrs)
    htmx["hx-headers"] = json.dumps(headers)
    attrs = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs}></div>"

def convert_generic(tag, attrs):
    htmx = build_htmx_attrs(**attrs)
    attrs_str = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attrs_str}></div>"

# ─────────────────────────────────────────────
#  Specialized converters (meta, chat, include, import, js)
# ─────────────────────────────────────────────
@register_hx_tag("meta")
def convert_meta(tag, attrs):
    tag_type = attrs.get("type", "meta")
    title, description = attrs.get("title"), attrs.get("description")
    name, content, data = attrs.get("name"), attrs.get("content"), attrs.get("data")
    element_id = attrs.get("id")
    frags = []
    if title: frags.append(f"<title>{title}</title>")
    if description: frags.append(f'<meta name="description" content="{description}">')
    if name and content: frags.append(f'<meta name="{name}" content="{content}">')
    if tag_type.lower() == "json" and data:
        frags.append(f'<script id="{element_id or "hx-data"}" type="application/json">{data}</script>')
    return "\n".join(frags)

@register_hx_tag("chat")
def convert_chat(tag, attrs):
    model = attrs.get("model", "gpt-4o-mini")
    title = attrs.get("title", "AI Chat Assistant")
    return f"""<div class="card shadow-lg border-0" id="aichat-card">
  <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
    <h5 class="mb-0"><i class="fas fa-robot me-2"></i>{title}</h5>
    <small class="text-muted">Model: {model}</small>
  </div>
  <div class="card-body" id="aichat-body" style="height:400px;overflow-y:auto;">
    <div class="text-muted text-center mt-5">Start chatting with {title}...</div>
  </div>
  <div class="card-footer bg-light">
    <form hx-post="/lti/developer/tools/aichat/send/" hx-target="#aichat-body" hx-swap="beforeend" hx-indicator=".chat-loader">
      <div class="input-group">
        <input type="text" name="prompt" class="form-control" placeholder="Type a message..." required />
        <button type="submit" class="btn btn-primary">Send</button>
      </div>
    </form>
    <div class="chat-loader text-center mt-2" style="display:none;">
      <i class="fas fa-spinner fa-spin"></i> Thinking...
    </div>
  </div>
</div>"""

@register_hx_tag("include")
def convert_include(tag, attrs):
    file_path = attrs.get("file")
    if not file_path:
        return "<!-- Missing file attribute in <hx:include> -->"
    ctx_str = attrs.get("context", "{}")
    try:
        local_ctx = json.loads(ctx_str.replace("'", '"')) if ctx_str else {}
    except Exception:
        local_ctx = {}
    try:
        return render_to_string(file_path, local_ctx)
    except Exception as e:
        return f"<!-- Failed to include {file_path}: {e} -->"

@register_hx_tag("import")
def convert_import(tag, attrs):
    css_links, js_scripts = [], []
    for css_file in attrs.get("css", "").split(","):
        css_file = css_file.strip()
        if css_file:
            css_links.append(f'<link rel="stylesheet" href="{css_file}">')
    for js_file in attrs.get("js", "").split(","):
        js_file = js_file.strip()
        if js_file:
            js_scripts.append(f'<script src="{js_file}"></script>')
    inline = attrs.get("inline")
    if inline:
        js_scripts.append(f"<script>{inline}</script>")
    return "\n".join(css_links + js_scripts)

@register_hx_tag("js")
def convert_js(tag, attrs):
    subtype = tag.name.split(":")[1]
    if subtype == "fetch":
        url, method, then = attrs.get("url"), attrs.get("method", "GET").upper(), attrs.get("then", "")
        return f"""
        <script>
        fetch("{url}", {{method:"{method}"}})
          .then(r=>r.text())
          .then(html=>{{const [sel,tgt] = "{then}".split(":"); if(sel==="render") document.querySelector(tgt).innerHTML = html;}});
        </script>
        """
    if subtype == "on":
        event, target, url = attrs.get("event","click"), attrs.get("target"), attrs.get("url","")
        return f"""
        <script>
        document.querySelector("{target}").addEventListener("{event}", async()=>{{
            const res = await fetch("{url}"); const html = await res.text();
            document.querySelector("{attrs.get('then','#output')}").innerHTML = html;
        }});
        </script>
        """
    return "<!-- Unknown hxjs subtype -->"

# ─────────────────────────────────────────────
#  {% hx %} compiler tag
# ─────────────────────────────────────────────
@register.tag(name="hx")
def do_hx(parser, token):
    bits = token.split_contents()
    debug = "debug=True" in bits
    nodelist = parser.parse(("endhx",))
    parser.delete_first_token()
    return HXNode(nodelist, debug)

class HXNode(template.Node):
    def __init__(self, nodelist, debug=False):
        self.nodelist, self.debug = nodelist, debug
    def render(self, context):
        rendered = self.nodelist.render(context)
        compiler = HyperXCompiler(rendered)
        _ = compiler.parse()
        soup = BeautifulSoup(rendered, "html.parser")
        for tag in soup.find_all(lambda t: t.name and t.name.startswith("hx:")):
            ttype = tag.name.split(":")[1]
            attrs = dict(tag.attrs)
            conv = TAG_CONVERTERS.get(ttype, convert_generic)
            tag.replace_with(BeautifulSoup(conv(tag, attrs), "html.parser"))
        html = str(soup)
        if self.debug:
            print("[HyperX Rendered HTML]\n", html)
        return mark_safe(html)

# ─────────────────────────────────────────────
#  Runtime helpers (auto-inject when DEBUG)
# ─────────────────────────────────────────────
@register.simple_tag
def hx_runtime_scripts():
    if not getattr(settings, "DEBUG", False):
        return ""
    scripts = [
        static("hxjs/loader.js"),
        static("hxjs/dragdrop.js"),
        static("hxjs/drawer.js"),
    ]
    tags = "\n".join(f'<script type="module" src="{src}"></script>' for src in scripts)
    return mark_safe(tags)
