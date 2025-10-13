from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-poll")
_logger.info("hx-poll initialized")




@register_hx_tag("poll")
def convert_poll(tag, attrs):
    """
    Usage:
      <hx:poll get="dashboard:update" every="5s" target="#stats" />
    """
    get = attrs.get("get")
    every = attrs.get("every", "10s")
    target = attrs.get("target", "#content")
    swap = attrs.get("swap", "innerHTML")

    return f'''
    <div hx-get="/{get}" hx-trigger="every {every}" hx-target="{target}" hx-swap="{swap}">
      <div class="text-muted small">
        <i class="fas fa-sync-alt fa-spin me-1"></i>Auto-updating every {every}
      </div>
    </div>
    '''
