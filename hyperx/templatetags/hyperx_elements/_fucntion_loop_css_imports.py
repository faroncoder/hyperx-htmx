from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-auto_css")
_logger.info("hx-auto_css initialized")

import os, sys, re
from django.conf import settings
from pathlib import Path
import logging



@register_hx_tag("auto_css")
def hx_auto_import_css(tag, attrs):
    """
    Dynamically auto-import all CSS files from static/css.
    Falls back gracefully if manage.py is not found or static dir is missing.
    """

    csstags = []

    # ───────────────────────────────
    # 1. Try to anchor from settings.BASE_DIR first
    # ───────────────────────────────
    try:
        base_dir = Path(settings.BASE_DIR)
        if not (base_dir / "manage.py").exists():
            raise FileNotFoundError
    except Exception:
        # ───────────────────────────────
        # 2. Fallback: walk up from this file
        # ───────────────────────────────
        current_dir = Path(__file__).resolve().parent
        base_dir = None
        for parent in [current_dir, *current_dir.parents]:
            if (parent / "manage.py").exists():
                base_dir = parent
                break

        if not base_dir:
            logging.warning("⚠️ manage.py not found — skipping CSS auto-import.")
            return ""

    # ───────────────────────────────
    # 3. Locate static/css and build import tags
    # ───────────────────────────────
    static_css = base_dir / "static" / "css"
    if static_css.is_dir():
        for filename in sorted(static_css.iterdir()):
            if filename.suffix == ".css":
                # Proper Django static template usage
                rel_path = f"css/{filename.name}"
                csstags.append(f'<hx:import src="{{% static \'{rel_path}\' %}}" />')
    else:
        logging.info(f"No CSS directory found at: {static_css}")

    return "\n".join(csstags)
