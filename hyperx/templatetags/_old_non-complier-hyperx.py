"""
hyperx/templatetags/hyperx.py
────────────────────────────────────────────
Declarative <hx:*> template tags for Django.

Usage:
    {% load hyperx %}
    {% hx %}
      <hx:panel get="lti:admin:course_table_view" target="#intel-container" swap="innerHTML" />
      <hx:button post="lti:teacher:sync_grades" confirm="Sync grades?" label="Sync Now" />
    {% endhx %}
"""

from django import template
from django.utils.safestring import mark_safe
from bs4 import BeautifulSoup
from hyperx.core import build_htmx_attrs

register = template.Library()

# ─────────────────────────────────────────────
# 🔧 Tag Registry
# ─────────────────────────────────────────────
TAG_CONVERTERS = {}

def register_hx_tag(tag_name):
    """Decorator for registering new <hx:*> tag converters."""
    def wrapper(func):
        TAG_CONVERTERS[tag_name] = func
        return func
    return wrapper


# ─────────────────────────────────────────────
# 🧩 Base Converters
# ─────────────────────────────────────────────
def convert_generic(tag, attrs):
    """Fallback converter for unknown <hx:*> tags."""
    htmx = build_htmx_attrs(**attrs)
    attr_str = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attr_str}></div>"


@register_hx_tag("panel")
def convert_panel(tag, attrs):
    """Convert <hx:panel> into a div with htmx attributes."""
    htmx = build_htmx_attrs(**attrs)
    attr_str = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<div {attr_str}></div>"


@register_hx_tag("button")
def convert_button(tag, attrs):
    """Convert <hx:button> into an interactive HTMX button."""
    label = attrs.get("label", "Action")
    htmx = build_htmx_attrs(**attrs)
    attr_str = " ".join(f'{k}="{v}"' for k, v in htmx.items())
    return f"<button {attr_str}>{label}</button>"


@register_hx_tag("xtab")
def convert_xtab(tag, attrs):
    """
    Generate an X-Tab reactive div:
    <hx:xtab name="student" function="crud" command="list" version="1" />
    """
    import json
    headers = {
        "X-Tab": f"{attrs.get('name')}:{attrs.get('version','1')}:{attrs.get('function')}:{attrs.get('command')}"
    }

    htmx = build_htmx_attrs(**attrs)
    htmx["hx-headers"] = json.dumps(headers)
    attr_str = " ".join(f'{k}="{v}"' for k, v in htmx.items())

    return f"<div {attr_str}></div>"


# ─────────────────────────────────────────────
# 🔨 Tag Processor
# ─────────────────────────────────────────────
def parse_hx_tag(tag):
    """Convert <hx:*> tags to their proper HTML equivalents."""
    tag_type = tag.name.split(":")[1]
    attrs = dict(tag.attrs)
    converter = TAG_CONVERTERS.get(tag_type, convert_generic)
    return converter(tag, attrs)


# ─────────────────────────────────────────────
# 🔄 {% hx %} ... {% endhx %}
# ─────────────────────────────────────────────
@register.tag(name="hx")
def do_hx(parser, token):
    """
    Process a declarative {% hx %} block.
    Recursively replaces all <hx:*> tags with HTMX-compatible markup.
    """
    nodelist = parser.parse(("endhx",))
    parser.delete_first_token()
    return HXNode(nodelist)


class HXNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        rendered = self.nodelist.render(context)
        soup = BeautifulSoup(rendered, "html.parser")

        changed = True
        while changed:
            changed = False
            for tag in soup.find_all(lambda t: t.name and t.name.startswith("hx:")):
                html = parse_hx_tag(tag)
                tag.replace_with(BeautifulSoup(html, "html.parser"))
                changed = True

        return mark_safe(str(soup))
