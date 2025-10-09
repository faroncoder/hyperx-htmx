from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

import json

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
    return attrs