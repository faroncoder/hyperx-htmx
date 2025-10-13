"""
django_helpers.py
──────────────────────────────────────────────
Centralized helper utilities for HyperX CLI commands.

Provides safe wrappers for:
  - Django settings detection
  - App + middleware inspection
  - File and environment helpers
  - Logging and summary formatting
"""

import os
import sys
import json
import importlib
from pathlib import Path
from django.conf import settings
from django.apps import apps
from datetime import datetime

# ───────────────────────────────────────────────
# 🔍 Django Environment Utilities
# ───────────────────────────────────────────────
def find_settings_path(settings_file: str = None, start_dir=".") -> Path | None:
    """
    Recursively search for settings.py file starting from start_dir.
    If settings_file is provided and exists, return its resolved path.
    """
    if settings_file:
        p = Path(settings_file)
        if p.exists():
            return p.resolve()

    # Check via DJANGO_SETTINGS_MODULE
    try:
        module = os.environ.get("DJANGO_SETTINGS_MODULE")
        if module:
            mod = importlib.import_module(module)
            return Path(mod.__file__).resolve()
    except Exception:
        pass

    # Recursively search for settings.py
    for root, dirs, files in os.walk(start_dir):
        if "settings.py" in files:
            return Path(root) / "settings.py"

    print("⚠️ Could not auto-detect Django settings path.")
    return None


def get_app_path(app_label: str) -> Path | None:
    """
    Get a Django app's filesystem path from its label.
    """
    try:
        app_module = importlib.import_module(app_label)
        return Path(app_module.__file__).resolve().parent
    except ModuleNotFoundError:
        print(f"❌ App '{app_label}' not found.")
        return None


def list_installed_apps():
    """Return a list of all INSTALLED_APPS."""
    try:
        return getattr(settings, "INSTALLED_APPS", [])
    except Exception:
        print("⚠️ Django settings not configured yet.")
        return []


def get_middlewares():
    """Return a list of all configured middlewares."""
    return getattr(settings, "MIDDLEWARE", [])


# ───────────────────────────────────────────────
# 🧩 Environment & File Utilities
# ───────────────────────────────────────────────

def ensure_directory(path: Path):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def timestamp():
    """Return an ISO-style timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_json(data, path: Path):
    """Write JSON data safely."""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Wrote JSON → {path}")
    except Exception as e:
        print(f"❌ Failed to write {path}: {e}")


# ───────────────────────────────────────────────
# 📦 Summaries & Diagnostics
# ───────────────────────────────────────────────

def summarize(title: str, data: dict, emoji="🧭"):
    """Pretty-print a simple key/value summary."""
    print(f"\n{emoji} {title}")
    print("─" * (len(title) + 4))
    for key, value in data.items():
        print(f"{key:<25}: {value}")
    print()


def print_success(msg: str):
    print(f"✅ {msg}")


def print_warning(msg: str):
    print(f"⚠️ {msg}")


def print_error(msg: str):
    print(f"❌ {msg}")


# ───────────────────────────────────────────────
# 🧰 Django Integration Checks
# ───────────────────────────────────────────────

def check_app_installed(app_name: str) -> bool:
    """Return True if an app is in INSTALLED_APPS."""
    return app_name in list_installed_apps()


def check_middleware_present(mw_name: str) -> bool:
    """Return True if middleware is configured."""
    return any(mw_name in mw for mw in get_middlewares())


def check_middleware_order():
    """Basic sanity check for HTMX → HyperX middleware ordering."""
    middleware = get_middlewares()
    order = {
        "csrf": next((i for i, m in enumerate(middleware) if "csrf" in m.lower()), -1),
        "htmx": next((i for i, m in enumerate(middleware) if "HtmxMiddleware" in m), -1),
        "hyperx": next((i for i, m in enumerate(middleware) if "HyperXMiddleware" in m), -1),
        "auth": next((i for i, m in enumerate(middleware) if "AuthenticationMiddleware" in m), -1),
    }

    if order["csrf"] < order["htmx"] < order["hyperx"] < order["auth"]:
        print_success("Middleware order appears correct.")
        return True
    else:
        print_warning("Middleware order may need adjustment.")
        print("Recommended order: CSRF → HTMX → HyperX → Auth")
        return False
