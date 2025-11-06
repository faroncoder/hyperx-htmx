# htmx_core/dispatchers/self_dispatcher.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpResponse
import json

class HyperXDispatcher(MiddlewareMixin):
    """
    Central orchestrator that decides how to respond based on request self-awareness.
    """

    def __init__(self, request):
        self.request = request

    def respond(self, template_name, context=None, status=200):
        from htmx_core.utils.htmx_response import hx_render
        from htmx_core.utils.htmx_helpers import hx_redirect, hx_trigger
        ctx = context or {}

        # Example behavior logic
        if self.request.htmx_type == "modal":
            return hx_render(self.request, template_name, ctx, status)
        elif self.request.htmx_type == "upload":
            return JsonResponse({"status": "uploaded"}, status=status)
        elif self.request.htmx_type == "search":
            return hx_render(self.request, template_name, ctx)
        else:
            return hx_render(self.request, template_name, ctx)
