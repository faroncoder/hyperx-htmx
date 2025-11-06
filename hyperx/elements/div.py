from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.logger.hx_logger import *
from hyperx.hx.hx_converter import register_hx_tag
from hyperx.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("BROKEN")
_logger.info("hx-crud initialized")


