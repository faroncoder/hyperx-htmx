# htmx_core/utils/decorators.py
from functools import wraps
from django.shortcuts import render
# redirect import removed - using HTMX client-side redirects instead
from django.urls import reverse
from htmx_core.utils.htmx_defaults import htmx_defaults
from htmx_core.functions.auth_forms import LoginForm

def htmx_login_required(view_func):
    """
    Enhanced version aware of self-type (form, modal, etc.).
    Renders login inline if HTMX request, otherwise redirects.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if getattr(request, "is_htmx", False):
                htmx_ctx = htmx_defaults(request, divplaceholder="#main-content")
                form = LoginForm(request=request)
                context = {
                    "title": "Login Required",
                    "form": form,
                    "message": "Please sign in to continue",
                    "login_submit_url": reverse("core:login_submit"),
                    "htmx_defaults": htmx_ctx["htmx_defaults"],
                    "htmx_self": getattr(request, "htmx_self", {}),
                }
                template = "core/auth/login_form_crispy.html"
                if getattr(request, "htmx_type", None) == "modal":
                    template = "core/auth/login_modal.html"
                return render(request, template, context)
            # SNUBBED: redirect(reverse("core:login_access_view")) -> HTMX client-side redirect
            from htmx_core.utils.htmx_helpers import _hx_redirect
            return _hx_redirect(reverse("core:login_access_view"))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
