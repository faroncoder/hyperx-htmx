"""
🚀 HyperX-HTMX Django Integration Settings
==========================================

This file shows how to integrate HyperX into your existing Django project.
Copy the relevant sections to your project's settings.py file.

Installation:
pip install django-htmx hyperx-htmx
"""

from dotenv import load_dotenv
import os
from pathlib import Path
from decouple import config

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "datasets"


# OpenAI API Key (for AI schema generation features)
OPENAI_API_KEY = config('OPENAI_API_KEY', default="")

# ==========================================
# 5. Optional: Enhanced Logging for HyperX
# ==========================================

# Add this to your existing LOGGING configuration:
HYPERX_LOGGING = {
    'hyperx': {
        'handlers': ['console', 'file'],  # Use your existing handlers
        'level': 'INFO',
        'propagate': False,
    },
    'hyperx.middleware': {
        'handlers': ['console'],
        'level': 'DEBUG' if config('DEBUG', default=False, cast=bool) else 'INFO',
        'propagate': False,
    },
}

# ==========================================
# Template Usage
# ==========================================
"""
In your templates, load the HyperX template tags:

{% load hyperx %}

{% hx %}
  <hx:button get="your_app:your_view" target="#content" label="Click Me" />
  <hx:panel get="your_app:dashboard" swap="innerHTML" target="#dashboard" />
{% endhx %}
"""

# ==========================================
# View Usage Example
# ==========================================
"""
In your views.py:

from hyperx import build_htmx_attrs, htmx_login_required, is_htmx_request

@htmx_login_required
def my_view(request):
    if is_htmx_request(request):
        # Return partial template for HTMX requests
        return render(request, 'partials/content.html', context)
    else:
        # Return full page for regular requests
        return render(request, 'pages/full_page.html', context)

def form_view(request):
    htmx_attrs = build_htmx_attrs(
        post='your_app:submit_form',
        target='#form-results',
        swap='outerHTML'
    )
    return render(request, 'form.html', {'htmx_attrs': htmx_attrs})
"""