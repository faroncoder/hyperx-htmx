"""
    <hx:upload>
    ─────────────────────────────────────────────
    Declarative file upload element integrated with AI dataset watcher.

    🧠 ATTRIBUTES
    • post="hyperx:upload_handler"
    • accept=".csv,.json"
    • autoschema="true|false"
    • label="Upload dataset"
    • target="#upload-status"

    🧩 EXAMPLE
    <hx:upload post="hyperx:upload_handler" accept=".csv,.json" autoschema="true" />
    """

from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-upload")
_logger.info("hx-upload initialized")




@register_hx_tag("upload")
def convert_upload(tag, attrs):


    post = attrs.get("post", "hyperx:upload_handler")  # Django route
    accept = attrs.get("accept", ".csv,.json")
    label = escape(attrs.get("label", "Upload file"))
    indicator = attrs.get("indicator", "")
    target = attrs.get("target", "#upload-status")
    autoschema = attrs.get("autoschema", "true").lower() in ("true", "1", "yes")

    autoschema_attr = f'data-autoschema="{str(autoschema).lower()}"'

    htmx_attrs = build_htmx_attrs(attrs, default_method="post", default_target=target)

    # ⚠️ note the doubled braces {{ }} inside JS — they survive the f-string!
    return f"""
<div class="hx-uploader border border-dashed rounded p-4 text-center"
     style="cursor:pointer;" {autoschema_attr}
     onclick="this.querySelector('input[type=file]').click();">
  <i class="fas fa-cloud-upload-alt fa-2x mb-2"></i>
  <p class="mb-1">{label}</p>
  <input type="file" name="file" accept="{accept}" class="d-none"
         hx-post="/{post}" hx-target="{target}" hx-swap="innerHTML"
         hx-indicator="{indicator}" />
</div>

<script type="text/javascript" src="{{% static 'js/hyperx-events.js' %}}"></script>

<script type="text/javascript">
const uploader = document.currentScript.previousElementSibling;
const input = uploader.querySelector('input[type=file]');
uploader.addEventListener('dragover', e => {{
    e.preventDefault(); uploader.classList.add('bg-light');
}});
uploader.addEventListener('dragleave', e => {{
    e.preventDefault(); uploader.classList.remove('bg-light');
}});
uploader.addEventListener('drop', e => {{
    e.preventDefault(); input.files = e.dataTransfer.files;
    htmx.trigger(input, 'change');
}});
</script>
"""
