"""
hyperx/templatetags/hyperx.py
────────────────────────────────────────────
Declarative <hx:*> template tag system with compiler integration.
Auto-includes Bootstrap, static, and runtime helpers.
"""
from django import template
register = template.Library()
from hyperx.logger.hx_logger import load_logger
from hyperx.hx.hx_converter import register_hx_tag
from hyperx.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
import hashlib
from django.conf import settings
from django.template import engines

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static as static_func
from django.template.loader import render_to_string
from django.template import engines
from django.template.library import import_library
from bs4 import BeautifulSoup
from hyperx.elements.generic import convert_generic 
from hyperx.bootstrap.bs_loader import initialize as bootstrap_initialize

_logger = load_logger("hyperx.templatetags.hyperx")
_logger.info("hyperx.templatetags.hyperx initializing")

from hyperx.hx.hx_actions_rules import build_htmx_attrs
from hyperx.hx.hx_converter import register_hx_tag
from hyperx.hx.hx_runtime_compiler import HyperXCompiler
from hyperx.loader.hx_loader import register_libraries 
from hyperx.hx.hx_converter import TAG_CONVERTERS




register = template.Library()

# autodiscover("hyperx.templatetags")

_logger.info("templatetags modules autodiscovered")




# ─────────────────────────────────────────────
#  Django built-ins
# ─────────────────────────────────────────────
@register.simple_tag
def static(path):
    return static_func(path)

# Register 'load static' so it's available when 'load hyperx' is used

# Register 'load static' so it's available when 'load hyperx' is used
if settings.configured:
    try:
        engines['django'].engine.template_libraries['static'] = 'django.templatetags.static'
        _logger.info("[HyperX] Django 'static' tag registered")
    except Exception as e:
        _logger.warning(f"[HyperX] Could not register 'static' tag: {e}")

    try:
        bootstrap_lib = import_library("django_bootstrap5")
        _logger.info("[HyperX] Bootstrap5 (django-bootstrap5) detected")
    except Exception:
        _logger.warning("[HyperX] django-bootstrap5 not found, trying django-bootstrap4...")
        try:
            bootstrap_lib = import_library("django_bootstrap4")
            _logger.info("[HyperX] Bootstrap4 (django-bootstrap4) detected")
        except Exception:
            bootstrap_lib = None
            _logger.warning("[HyperX] django-bootstrap5 and django-bootstrap4 not found, Bootstrap tags unavailable")

    if bootstrap_lib:
        for n, t in getattr(bootstrap_lib, "tags", {}).items():
            register.tag(n, t)
            tags = getattr(t, "tags", [])
            for tag in tags:
                register.tag(tag, getattr(t, tag))
                _logger.info(f"[HyperX] Bootstrap tag '{tag}' registered")

        for n, f in getattr(bootstrap_lib, "filters", {}).items():
            register.filter(n, f)
            filters = getattr(f, "filters", [])
            for flt in filters:
                register.filter(flt, getattr(f, flt))
                _logger.info(f"[HyperX] Bootstrap filter '{flt}' registered")

        _logger.info("[HyperX] Bootstrap tags merged")
    else:
        _logger.warning("[HyperX] Bootstrap not found")
else:
    _logger.debug("[HyperX] Django settings not configured; skipping static and Bootstrap tag registration.")

# ─────────────────────────────────────────────
#  Tag converter registry
# ─────────────────────────────────────────────



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
        static("hxjs/hyperx-events.js"),
        static("hxjs/hyperx-core.js"),
    ]
    tags = "\n".join(f'<script type="module" src="{src}"></script>' for src in scripts)
    return mark_safe(tags)





def make_hx_pair(user_id, secret):
    token = hashlib.sha1(f"{user_id}{secret}".encode()).hexdigest()[:12]
    return f"HX-{token}"