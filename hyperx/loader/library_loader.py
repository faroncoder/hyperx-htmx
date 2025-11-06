#!/usr/bin/env python3
"""
library_loader.py
──────────────────────────────
Generic loader for multiple Django template tag libraries.
Reads configuration from a YAML file and registers them dynamically.
"""

import os, sys, yaml, django
from pathlib import Path
from django import template
from django.template.library import import_library
from hyperx.logger.hx_logger import load_logger

_logger = load_logger("hx.library_loader")
_logger.info("hx.library_loader initialized")

# Django template registration object
register = template.Library()

# ─────────────────────────────
# 1. Config path detection
# ─────────────────────────────
config_path = Path(
    os.getenv("HYPERX_LIB_CONFIG", Path(__file__).parent / "hyperx_config.yaml")
)
_logger.info(f"[HyperX] Using config path: {config_path}")

# ─────────────────────────────
# 2. Load YAML configuration
# ─────────────────────────────
def load_config(yaml_path: Path):
    """Read YAML configuration file listing libraries to register."""
    if not Path(yaml_path).exists():
        _logger.error(f"[HyperX] Config file not found: {yaml_path}")
        return []
    try:
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f) or {}
        libs = config.get("libraries", [])
        _logger.info(f"[HyperX] Found {len(libs)} libraries in config: {libs}")
        return libs
    except Exception as e:
        _logger.error(f"[HyperX] Failed to read config: {e}", exc_info=True)
        return []

# ─────────────────────────────
# 3. Register template libraries
# ─────────────────────────────
def register_libraries(lib_names):
    """Import and register multiple Django template tag libraries."""
    for lib_name in lib_names:
        try:
            lib = import_library(lib_name)
            _logger.info(f"[HyperX] {lib_name} imported successfully")

            if hasattr(lib, "tags"):
                for tag_name, tag_func in lib.tags.items():
                    register.tag(tag_name, tag_func)
                    _logger.debug(f"[HyperX] {lib_name}: tag registered -> {tag_name}")

            if hasattr(lib, "filters"):
                for filter_name, filter_func in lib.filters.items():
                    register.filter(filter_name, filter_func)
                    _logger.debug(f"[HyperX] {lib_name}: filter registered -> {filter_name}")

            _logger.info(f"[HyperX] {lib_name}: tags and filters registered")
        except Exception as e:
            _logger.error(f"[HyperX] Failed to import {lib_name}: {e}", exc_info=True)

    return register

# ─────────────────────────────
# 4. CLI / Standalone execution
# ─────────────────────────────
if __name__ == "__main__":
    if not django.apps.apps.ready:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        try:
            django.setup()
        except Exception as e:
            _logger.warning(f"[HyperX] Django setup skipped or failed: {e}")

    libs = load_config(config_path)
    if not libs:
        _logger.warning("[HyperX] No libraries found in YAML config.")
        sys.exit(1)

    _logger.info(f"[HyperX] Registering {len(libs)} libraries...")
    register_libraries(libs)
    print("✅  Libraries registered dynamically from YAML.")

def init_hx():
    """Initialize HX runtime (called by bs_loader)."""
    _logger.info("[HXLoader] ✅ HX runtime initialized.")
    return True
