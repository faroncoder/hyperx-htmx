from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-forms")
logger_htmx_forms = load_logger("htmx-forms")




def htmx_form_submit(form_url, target_id='#form-container'):
    """Predefined HTMX config for form submissions"""
    logger_htmx_forms.debug(f"Creating form submit HTMX config: url={form_url}, target={target_id}")
    
    attrs = build_htmx_attrs(
        post=form_url,
        trigger='submit',
        target=target_id,
        swap='outerHTML',
        indicator='#form-loading',
        on_before_request="disableFormButtons()",
        on_after_request="enableFormButtons()"
    )
    
    logger_htmx_forms.info(f"Form submit HTMX config created: url={form_url}, target={target_id}")
    return

