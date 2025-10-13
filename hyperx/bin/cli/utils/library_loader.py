"""
library_loader.py
──────────────────────────────
Generic loader for multiple Django template tag libraries.
Reads configuration from a YAML file.
"""

import os
import sys
import yaml
import django
from django import template
from django.template.library import import_library
from hyperx.bin.cli.logger.hx_logger import *

_logger = load_logger("library_registration")
_logger.info("library_registration initialized")

register = template.Library()

def load_config(yaml_path: str):
    """Read YAML configuration file listing libraries to register."""
    path = os.path.expanduser(yaml_path)
    if not os.path.exists(path):
        _logger.critical(f"[HyperX] Config file not found: {path}")
        return []
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f) or {}
            libs = config.get("libraries", [])
            _logger.info(f"[HyperX] Found {len(libs)} libraries in config: {libs}")
            return libs
    except Exception as e:
        _logger.critical(f"[HyperX] Failed to read config: {e}")
        return []


def register_libraries(lib_names):
    """Import and register multiple Django template libraries."""
    for lib_name in lib_names:
        try:
            lib = import_library(lib_name)
            _logger.info(f"[HyperX] {lib_name} imported successfully")

            for tag_name, tag_func in getattr(lib, "tags", {}).items():
                register.tag(tag_name, tag_func)
                _logger.debug(f"[HyperX] {lib_name}: tag registered -> {tag_name}")

            for filter_name, filter_func in getattr(lib, "filters", {}).items():
                register.filter(filter_name, filter_func)
                _logger.debug(f"[HyperX] {lib_name}: filter registered -> {filter_name}")

            _logger.info(f"[HyperX] {lib_name} tags and filters registered")

        except Exception as e:
            _logger.error(f"[HyperX] Failed to import {lib_name}: {e}", exc_info=True)

    return register


if __name__ == "__main__":
    # Tell Django which settings to use
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hyperx_project.settings")
    django.setup()

    # Path to YAML config (relative or absolute)
    config_file = os.getenv("HYPERX_LIB_CONFIG", "hyperx_config.yml")

    libs = load_config(config_file)
    if not libs:
        _logger.warning("[HyperX] No libraries found in YAML config.")
        sys.exit(1)

    _logger.info(f"[HyperX] Registering {len(libs)} libraries...")
    register_libraries(libs)
    print("✅  Libraries registered dynamically from YAML.")
