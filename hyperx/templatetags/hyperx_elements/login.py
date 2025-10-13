from django import template
from django.shortcuts import render
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-login")
_logger.info("hx-login initialized")

from functools import wraps
from django.http import HttpResponse


import os
from pathlib import Path
import json
#from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

def htmx_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get("HX-Request") == "true":
                # Try primary template
                try:
                    return render(
                        request,
                        "core/auth/login_form_crispy.html",
                        {
                            "title": "Login Required",
                            "login_url": reverse("core:login_access_view"),
                        },
                    )
                except Exception:
                    # Render fallback template instead of inline HTML
                    html = render_to_string(
                        "core/htmx/login_fallback.html",
                        {"login_url": reverse("core:login_access_view")},
                    )
                    return HttpResponse(html)
            # Normal request: redirect
            return render("core:login_access_view")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

