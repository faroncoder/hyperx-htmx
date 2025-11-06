# htmx_core/utils/hyperx_response.py
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# redirect import removed - using HTMX client-side redirects instead
from django.urls import reverse

def hx_render(request, template_name, context=None, status=200):
    """
    Smart render that respects HTMX awareness.
    Uses request.htmx_type and request.htmx_self for adaptive behavior.
    """
    context = context or {}

    # Optionally inject htmx_self context for introspection in templates
    if hasattr(request, "htmx_self") and request.htmx_self:
        context["htmx_self"] = request.htmx_self

    if getattr(request, "is_htmx", False):
        # If it's a modal request, you could apply a template namespace rule
        if request.htmx_type == "modal":
            template_name = template_name.replace(".html", "_modal.html")
        return render(request, template_name, context=context, status=status)
    return render(request, template_name, context=context, status=status)


# NOTE: hx_redirect and hx_trigger moved to htmx_orphaned_snippets.py
# These functions are duplicated in htmx_helpers.py - use those versions instead
# or enable DUPLICATE_RESPONSE_HELPERS in htmx_orphaned_snippets.py for testing
