from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-chat")
_logger.info("hx-chat initialized")


@register_hx_tag("chat")
def convert_chat(tag, attrs):
    model = attrs.get("model", "gpt-4o-mini")
    title = attrs.get("title", "AI Chat Assistant")
    channel = attrs.get("channel", "default")
    room_id = escape(channel.replace(" ", "_").lower())
    send_url = attrs.get("send", "/lti/developer/tools/aichat/send/")
    room_target = f"#aichat-body-{room_id}"

    return f"""
    <div class="card shadow-lg border-0 mb-3" id="aichat-card-{room_id}">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fas fa-robot me-2"></i>{title}</h5>
        <small class="text-muted">Model: {model} | Channel: {channel}</small>
      </div>

      <div class="card-body" id="aichat-body-{room_id}" style="height: 300px; overflow-y: auto;">
        <div class="text-muted text-center mt-5">
          Enter your message to start chat in <b>{channel}</b>.
        </div>
      </div>

      <div class="card-footer bg-light">
        <form
          hx-post="{send_url}"
          hx-vals='{{"channel": "{channel}"}}'
          hx-target="{room_target}"
          hx-swap="beforeend"
          hx-indicator=".chat-loader-{room_id}"
        >
          <div class="input-group">
            <input type="text" name="prompt" class="form-control"
                   placeholder="Message {channel}..." required />
            <button type="submit" class="btn btn-primary">Send</button>
          </div>
        </form>
        <div class="chat-loader-{room_id} text-center mt-2" style="display:none;">
          <i class="fas fa-spinner fa-spin"></i> Thinking...
        </div>
      </div>
    </div>

    <script>
      document.body.addEventListener("aichat:new", function(e) {{
        const data = e.detail;
        const room = data.channel || "default";
        if (room !== "{channel}") return;
        const body = document.querySelector("{room_target}");
        if (!body) return;
        const msg = document.createElement("div");
        msg.className = "chat-bubble bg-primary text-white p-2 rounded my-1";
        msg.textContent = data.content;
        body.appendChild(msg);
        body.scrollTop = body.scrollHeight;
      }});
    </script>
    """