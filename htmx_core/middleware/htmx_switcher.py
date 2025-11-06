# htmx_core/middleware/htmx_switcher.py
import json
from django.utils.deprecation import MiddlewareMixin

class HTMXRequestSwitcher(MiddlewareMixin):
    """
    Middleware to classify incoming HTMX or HyperX requests based on custom X-<Type>-Request headers.
    Attaches structured metadata to the request object for intelligent routing and security policies.
    """

    # Define all known HTMX request types
    SUPPORTED_TYPES = {
        "X-General-Request": "general",
        "X-Form-Request": "form",
        "X-Upload-Request": "upload",
        "X-Search-Request": "search",
        "X-Menu-Request": "menu",
        "X-Modal-Request": "modal",
        "X-Clean-Request": "clean",
    }

    def process_request(self, request):
        # Default metadata
        request.is_htmx = request.headers.get("HX-Request", "").lower() == "true"
        request.htmx_type = None
        request.htmx_context = {}

        # Identify HTMX request type by scanning headers
        for header_name, req_type in self.SUPPORTED_TYPES.items():
            if request.headers.get(header_name):
                request.htmx_type = req_type
                break

        # If we found a type, build the context
        if request.htmx_type:
            request.htmx_context = self._extract_htmx_context(request)

        # Optional: automatically set flag for convenience
        request.is_modal = request.htmx_type == "modal"
        request.is_form = request.htmx_type == "form"
        request.is_upload = request.htmx_type == "upload"
        request.is_menu = request.htmx_type == "menu"
        request.is_search = request.htmx_type == "search"
        request.is_clean = request.htmx_type == "clean"

    def _extract_htmx_context(self, request):
        """
        Extracts token and routing metadata from headers.
        Returns a structured dict.
        """
        ctx = {}
        for key, value in request.headers.items():
            if key.startswith("X-"):
                ctx[key] = value
        # Optionally parse the HX headers JSON if sent as a string
        hx_headers = request.headers.get("HX-Headers")
        if hx_headers:
            try:
                ctx.update(json.loads(hx_headers))
            except json.JSONDecodeError:
                pass
        return ctx
