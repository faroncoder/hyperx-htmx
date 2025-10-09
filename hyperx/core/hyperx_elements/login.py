from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape


#from django.shortcuts import render
from django.template.loader import render_to_string

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
            return redirect("core:login_access_view")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


