"""
    <hx:pagination>
    ─────────────────────────────────────────────
    Declarative pagination component.

    🧠 ATTRIBUTES
    • source="users:list" → URL or view to fetch.
    • current="1" → Current page.
    • total="10" → Total pages.
    • target="#table" → Where to inject.

    🧩 EXAMPLE
    <hx:pagination source="users:list" current="3" total="12" target="#table" />
    """

from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-pagination")
_logger.info("hx-pagination initialized")



@register_hx_tag("pagination")
def convert_pagination(tag, attrs):
    
    from django.urls import reverse
    current = int(attrs.get("current", 1))
    total = int(attrs.get("total", 1))
    source = attrs.get("source")
    target = attrs.get("target", "#content")
    swap = attrs.get("swap", "innerHTML")
    size = attrs.get("size", "").lower()

    size_class = f"pagination-{size}" if size in ("sm", "small", "lg", "large") else ""

    prev_page = current - 1 if current > 1 else None
    next_page = current + 1 if current < total else None

    def page_link(page, label, disabled=False, active=False):
        if disabled:
            return f'<li class="page-item disabled"><span class="page-link">{label}</span></li>'
        if active:
            return f'<li class="page-item active"><a class="page-link" href="#">{label}</a></li>'
        return (
            f'<li class="page-item">'
            f'<a class="page-link" hx-get="/{source}?page={page}" '
            f'hx-target="{target}" hx-swap="{swap}">{label}</a>'
            f'</li>'
        )

    html = '<nav aria-label="Pagination"><ul class="pagination justify-content-center {0}">'.format(size_class)

    # previous
    html += page_link(prev_page, "&laquo; Prev", disabled=prev_page is None)

    # center pages (up to 5 window)
    window = range(max(1, current - 2), min(total + 1, current + 3))
    for p in window:
        html += page_link(p, p, active=(p == current))

    # next
    html += page_link(next_page, "Next &raquo;", disabled=next_page is None)
    html += "</ul></nav>"

    return html