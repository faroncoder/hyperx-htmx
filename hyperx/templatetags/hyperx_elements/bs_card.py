from django import template
register = template.Library()
from hyperx.templatetags.hyperx import register_hx_tag, build_htmx_attrs
from django.utils.html import escape
from django.conf import settings
from django.templatetags.static import static
import os
from pathlib import Path
import json