
from django import template
from django.urls import reverse
from django.utils.html import escape
from hyperx.bin.cli.logger.hx_logger import load_logger
import json
import logging

register = template.Library()
_logger = load_logger("hx_converter")
_logger.info("hx_converter initialized")

# ─────────────────────────────────────────────
# Tag registration
# ─────────────────────────────────────────────
TAG_CONVERTERS = {}

def register_hx_tag(tag_name):
    """Decorator to register a custom <hx:*> tag converter."""
    def wrapper(func):
        TAG_CONVERTERS[tag_name] = func
        _logger.debug(f"[HyperX Elements] Registered tag converter: {tag_name}")
        return func
    return wrapper

