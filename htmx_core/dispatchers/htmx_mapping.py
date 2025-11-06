# htmx_core/dispatchers/htmx_mapping.py
from django.http import JsonResponse, HttpResponse
import json

class HyperXDispatcher:
    RESPONSE_MAP = {
        "modal": "render_modal",
        "upload": "handle_upload",
        "search": "render_search",
        "form": "render_form",
    }

    def __init__(self, request):
        self.request = request

    def respond(self, template_name, context=None, status=200):
        ctx = context or {}
        handler_name = self.RESPONSE_MAP.get(self.request.htmx_type, "render_default")
        handler = getattr(self, handler_name, self.render_default)
        return handler(template_name, ctx, status)

    # --- Handlers ---
    def render_modal(self, template, ctx, status):
        from htmx_core.utils.htmx_response import hx_render
        return hx_render(self.request, template, ctx, status)

    def handle_upload(self, template, ctx, status):
        return JsonResponse({"status": "uploaded"}, status=status)

    def render_search(self, template, ctx, status):
        from htmx_core.utils.htmx_response import hx_render
        return hx_render(self.request, template, ctx)

    def render_default(self, template, ctx, status):
        from htmx_core.utils.htmx_response import hx_render
        return hx_render(self.request, template, ctx, status)
