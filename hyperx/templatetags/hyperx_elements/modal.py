from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-modal")
_logger.info("hx-modal initialized")



@register_hx_tag("modal")
def convert_modal(tag, attrs):
    """
    Usage:
      <hx:modal id="editUser" title="Edit User" size="lg" show="false">
        <hx:form post="users:update" target="#users-table">
          <hx:field label="Name" name="name" required="true" />
          <hx:field label="Email" name="email" />
        </hx:form>
      </hx:modal>
    """
    modal_id = attrs.get("id", "modal")
    title = escape(attrs.get("title", "Dialog"))
    size = attrs.get("size", "")
    show = attrs.get("show", "false").lower() in ("true", "1", "yes")

    size_class = f"modal-{size}" if size in ("sm", "lg", "xl") else ""
    inner_html = tag.decode_contents() or "<!-- modal content -->"

    return f"""
    <div class="modal fade {'show' if show else ''}" id="{modal_id}" tabindex="-1" role="dialog">
      <div class="modal-dialog {size_class}" role="document">
        <div class="modal-content">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title">{title}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">{inner_html}</div>
        </div>
      </div>
    </div>
    """
