"""
HTMX Template Tags
================

Custom Django template tags for HTMX Core functionality.
"""

from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
import json

# Create the template library
register = template.Library()


@register.simple_tag
def htmx_headers():
    """Generate HTMX-related HTML headers"""
    return mark_safe('''
    <meta name="htmx-config" content='{"globalViewTransitions": true}'>
    <meta name="htmx-ext" content="debug">
    ''')


@register.simple_tag
def htmx_csrf_headers(request):
    """Generate CSRF headers for HTMX requests"""
    if hasattr(request, 'META'):
        csrf_token = request.META.get('CSRF_COOKIE', '')
        return mark_safe(f'<meta name="csrf-token" content="{csrf_token}">')
    return ''


@register.simple_tag
def htmx_config(**kwargs):
    """Generate HTMX configuration as JSON"""
    default_config = {
        'timeout': 10000,
        'defaultSwapStyle': 'innerHTML',
        'defaultSwapDelay': 0,
        'defaultSettleDelay': 20,
        'includeIndicatorStyles': True
    }
    
    # Merge with provided kwargs
    config = {**default_config, **kwargs}
    
    return mark_safe(f'<script>htmx.config = {json.dumps(config)};</script>')


@register.simple_tag
def htmx_boost_links():
    """Enable HTMX boost for all links"""
    return mark_safe('<body hx-boost="true">')


@register.simple_tag
def htmx_target(value):
    """Generate hx-target attribute"""
    if not value.startswith('#') and not value.startswith('.') and value != 'this' and not value.startswith('closest'):
        value = f"#{value}"
    return mark_safe(f'hx-target="{value}"')


@register.simple_tag
def htmx_swap_oob(target_id, content=""):
    """Generate HTMX out-of-band swap directive"""
    return mark_safe(f'<div id="{target_id}" hx-swap-oob="true">{content}</div>')


@register.simple_tag
def htmx_trigger(event_name, target=None):
    """Generate HTMX trigger event"""
    if target:
        return mark_safe(f'hx-trigger="{event_name}" hx-target="{target}"')
    return mark_safe(f'hx-trigger="{event_name}"')


@register.inclusion_tag('htmx_core/partials/loading_indicator.html', takes_context=True)
def htmx_loading_indicator(context, target=None, message="Loading..."):
    """Render an HTMX loading indicator"""
    return {
        'target': target or '#main-content',
        'message': message,
        'request': context.get('request')
    }


@register.simple_tag
def htmx_polling(url, interval="5s", target=None):
    """Generate HTMX polling attributes"""
    attrs = f'hx-get="{url}" hx-trigger="every {interval}"'
    if target:
        attrs += f' hx-target="{target}"'
    return mark_safe(attrs)


@register.simple_tag
def htmx_confirm(message):
    """Generate HTMX confirmation dialog"""
    return mark_safe(f'hx-confirm="{message}"')


@register.filter
def htmx_indicator(element_id):
    """Convert element ID to HTMX indicator format"""
    return f"#{element_id}"


@register.simple_tag
def htmx_delete_confirm(url, target, message="Are you sure you want to delete this item?"):
    """Generate delete confirmation with HTMX"""
    return mark_safe(f'''
        hx-delete="{url}" 
        hx-target="{target}" 
        hx-confirm="{message}"
        hx-swap="outerHTML"
    ''')


@register.simple_tag
def htmx_form_submit(target="#main-content", swap="innerHTML"):
    """Generate HTMX form submission attributes"""
    return mark_safe(f'hx-target="{target}" hx-swap="{swap}"')


@register.simple_tag
def htmx_lazy_load(url, trigger="revealed"):
    """Generate HTMX lazy loading attributes"""
    return mark_safe(f'hx-get="{url}" hx-trigger="{trigger}"')


@register.simple_tag(takes_context=True)
def htmx_url(context, view_name, *args, **kwargs):
    """Generate URL for HTMX requests with proper context"""
    request = context.get('request')
    url = reverse(view_name, args=args, kwargs=kwargs)
    
    # Add HTMX header indication if needed
    if request and request.htmx:
        return url
    return url


@register.simple_tag
def htmx_websocket(url):
    """Generate HTMX WebSocket connection"""
    return mark_safe(f'hx-ws="connect:{url}"')


@register.filter
def is_htmx(request):
    """Check if request is from HTMX"""
    return getattr(request, 'htmx', False)


@register.simple_tag
def htmx_redirect(url):
    """Generate HTMX redirect header"""
    return mark_safe(f'HX-Redirect: {url}')


@register.simple_tag
def htmx_refresh():
    """Generate HTMX refresh directive"""
    return mark_safe('HX-Refresh: true')


# Register additional utility functions
@register.simple_tag
def htmx_version():
    """Return HTMX version info"""
    return mark_safe('<script>console.log("HTMX Version:", htmx.version || "Unknown");</script>')


@register.simple_tag
def htmx_debug(enabled=True):
    """Enable/disable HTMX debugging"""
    if enabled and settings.DEBUG:
        return mark_safe('<script>htmx.logger = console.log;</script>')
    return ''


# 🚀 MISSING HYPERX TEMPLATE TAGS - COMPLETE THE REVOLUTION! 🚀

@register.simple_tag
def htmx_get(url):
    """Generate hx-get attribute"""
    return mark_safe(f'hx-get="{url}"')

@register.simple_tag
def htmx_post(url):
    """Generate hx-post attribute"""  
    return mark_safe(f'hx-post="{url}"')

@register.simple_tag
def htmx_swap(mode):
    """Generate hx-swap attribute"""
    return mark_safe(f'hx-swap="{mode}"')

@register.simple_tag
def htmx_put(url):
    """Generate hx-put attribute"""
    return mark_safe(f'hx-put="{url}"')

@register.simple_tag
def htmx_delete(url):
    """Generate hx-delete attribute"""
    return mark_safe(f'hx-delete="{url}"')

@register.simple_tag
def htmx_patch(url):
    """Generate hx-patch attribute"""
    return mark_safe(f'hx-patch="{url}"')

@register.simple_tag
def htmx_encoding(encoding_type):
    """Generate hx-encoding attribute for file uploads"""
    return mark_safe(f'hx-encoding="{encoding_type}"')

@register.simple_tag
def htmx_params(params):
    """Generate hx-params attribute"""
    return mark_safe(f'hx-params="{params}"')

@register.simple_tag
def htmx_vals(vals):
    """Generate hx-vals attribute"""
    return mark_safe(f'hx-vals="{vals}"')

@register.simple_tag
def htmx_script(src=None, static_file=None):
    """Generate script tag for HTMX or custom scripts with static file support"""
    from django.templatetags.static import static
    
    if static_file:
        src = static(static_file)
        return mark_safe(f'<script src="{src}"></script>')
    elif src:
        return mark_safe(f'<script src="{src}"></script>')
    return mark_safe('<script src="https://unpkg.com/htmx.org@latest"></script>')

@register.simple_tag  
def htmx_style(href=None, static_file=None, content=None):
    """Generate style tag or link for CSS with static file support"""
    from django.templatetags.static import static
    
    if static_file:
        href = static(static_file)
        return mark_safe(f'<link rel="stylesheet" href="{href}">')
    elif href:
        return mark_safe(f'<link rel="stylesheet" href="{href}">')
    elif content:
        return mark_safe(f'<style>{content}</style>')
    return mark_safe('<style>.htmx-indicator { opacity: 0; transition: opacity 0.3s ease; } .htmx-request .htmx-indicator { opacity: 1; }</style>')

@register.simple_tag
def htmx_meta(name, content):
    """Generate meta tag for HTMX configuration"""
    return mark_safe(f'<meta name="{name}" content="{content}">')

@register.simple_tag
def htmx_link(rel, href, **attrs):
    """Generate link tag with optional attributes"""
    attr_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items()])
    return mark_safe(f'<link rel="{rel}" href="{href}" {attr_str}>'.strip())

@register.simple_tag
def htmx_on(event, handler):
    """Generate hx-on attribute for event handling"""
    return mark_safe(f'hx-on::{event}="{handler}"')

@register.simple_tag
def htmx_trigger(trigger):
    """Generate hx-trigger attribute"""
    return mark_safe(f'hx-trigger="{trigger}"')

@register.simple_tag
def htmx_target(target):
    """Generate hx-target attribute"""
    return mark_safe(f'hx-target="{target}"')

@register.simple_tag
def htmx_include(include):
    """Generate hx-include attribute"""
    return mark_safe(f'hx-include="{include}"')

@register.simple_tag
def htmx_confirm(message):
    """Generate hx-confirm attribute"""
    return mark_safe(f'hx-confirm="{message}"')

@register.simple_tag
def htmx_boost_links():
    """Generate hx-boost attribute for body/container"""
    return mark_safe('hx-boost="true"')

@register.simple_tag
def htmx_loading_indicator(target):
    """Generate hx-indicator attribute"""
    return mark_safe(f'hx-indicator="{target}"')

@register.simple_tag
def htmx_delete_confirm(url, target, confirm_msg):
    """Generate complete delete confirmation with hx-delete"""
    return mark_safe(f'hx-delete="{url}" hx-target="{target}" hx-confirm="{confirm_msg}" hx-swap="delete"')

@register.simple_tag
def htmx_prevent_default():
    """Generate hx-on attribute to prevent default form submission"""
    return mark_safe('hx-on::submit="event.preventDefault()"')

@register.simple_tag
def htmx_sync(sync_value):
    """Generate hx-sync attribute"""
    return mark_safe(f'hx-sync="{sync_value}"')

@register.simple_tag
def htmx_disable_during_request():
    """Generate hx-disabled-elt attribute to disable form during request"""
    return mark_safe('hx-disabled-elt="this"')

@register.simple_tag
def htmx_history(action):
    """Generate hx-history attribute"""
    return mark_safe(f'hx-history="{action}"')

@register.simple_tag
def htmx_push_url(url=None):
    """Generate hx-push-url attribute"""
    if url:
        return mark_safe(f'hx-push-url="{url}"')
    return mark_safe('hx-push-url="true"')

@register.simple_tag
def htmx_select(selector):
    """Generate hx-select attribute"""
    return mark_safe(f'hx-select="{selector}"')

@register.simple_tag
def htmx_select_oob(selector):
    """Generate hx-select-oob attribute"""
    return mark_safe(f'hx-select-oob="{selector}"')

@register.simple_tag
def htmx_timeout(timeout):
    """Generate hx-timeout attribute"""
    return mark_safe(f'hx-timeout="{timeout}"')


@register.inclusion_tag("htmx_core/partials/htmx_tabs.html", takes_context=True)
def htmx_tabs(context, tabs, target="#extended_content", default=None, base_url="/tab/"):
    """
    Render an HTMX tab system with HyperX compatibility.
    
    Example:
        {% htmx_tabs tabs="overview,reports,settings,activity" target="#extended_content" %}
    """
    if isinstance(tabs, str):
        tab_list = [t.strip() for t in tabs.split(",")]
    else:
        tab_list = tabs

    # Normalize default tab
    default_tab = default or (tab_list[0] if tab_list else None)

    return {
        "tabs": tab_list,
        "target": target,
        "default_tab": default_tab,
        "base_url": base_url,
        "request": context.get("request"),
    }




from django.template import Library, Node, TemplateSyntaxError
from django.utils.html import escape

class HXTabsNode(Node):
    def __init__(self, nodelist, tabset_id, target, default):
        self.nodelist = nodelist
        self.tabset_id = tabset_id
        self.target = target
        self.default = default

    def render(self, context):
        raw = self.nodelist.render(context)
        # Parse <hx:tab .../> definitions
        import re
        tab_pattern = re.compile(r'<hx:tab\s+([^>]+?)/?>', re.IGNORECASE)
        tabs = []
        for match in tab_pattern.findall(raw):
            attrs = dict(re.findall(r'(\w+)="([^"]+)"', match))
            tabs.append(attrs)

        target = self.target.resolve(context)
        tabset_id = self.tabset_id.resolve(context)
        default = self.default.resolve(context) if self.default else (tabs[0]["name"] if tabs else "")

        # Build tab markup
        html = [f'<ul class="nav nav-tabs" id="{tabset_id}">']
        for tab in tabs:
            name = escape(tab.get("name"))
            label = escape(tab.get("label", name.title()))
            active = "active" if name == default else ""
            html.append(
                f'<li class="nav-item">'
                f'<a class="nav-link {active}" '
                f'hx-get="/tab/{name}/" '
                f'hx-target="{target}" '
                f'hx-swap="innerHTML">{label}</a></li>'
            )
        html.append("</ul>")

        # Content container
        target_id = target.lstrip("#")
        html.append(
            f'<div id="{target_id}" class="mt-3">'
            f'<div hx-get="/tab/{default}/" hx-trigger="load" '
            f'hx-target="{target}" hx-swap="innerHTML"></div>'
            f'</div>'
        )

        # Auto-update active class after swap
        html.append(f"""
        <script>
        document.body.addEventListener('htmx:afterSwap', (e) => {{
          if (e.detail.target.id === '{target_id}') {{
            document.querySelectorAll('#{tabset_id} .nav-link').forEach(a => a.classList.remove('active'));
            const link = document.querySelector(`#{{tabset_id}} .nav-link[hx-get="{{e.detail.xhr.responseURL}}"]`);
            if (link) link.classList.add('active');
          }}
        }});
        </script>
        """)
        return "".join(html)


@register.tag(name="hx_tabs")
def do_hx_tabs(parser, token):
    """
    Declarative <hx:tabs> block tag parser.
    Usage:
        {% hx_tabs id="main-tabs" target="#extended_content" default="overview" %}
            <hx:tab name="overview" label="Overview" />
            <hx:tab name="reports" label="Reports" />
        {% endhx_tabs %}
    """
    bits = token.split_contents()
    tag_name = bits[0]
    kwargs = {}
    for bit in bits[1:]:
        key, val = bit.split("=", 1)
        kwargs[key] = parser.compile_filter(val)

    nodelist = parser.parse(("endhx_tabs",))
    parser.delete_first_token()

    if "id" not in kwargs or "target" not in kwargs:
        raise TemplateSyntaxError(f"{tag_name} requires id and target attributes")

    return HXTabsNode(
        nodelist,
        tabset_id=kwargs["id"],
        target=kwargs["target"],
        default=kwargs.get("default"),
    )



