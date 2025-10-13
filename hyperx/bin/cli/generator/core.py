import sys
from pathlib import Path
from django.apps import apps
import importlib

from hyperx.bin.cli.generator.htmx_backend_dashboard import *
from hyperx.bin.cli.generator.htmx_backend_views import *
from hyperx.bin.cli.generator.htmx_backend_urls import *
from hyperx.bin.cli.logger.hx_logger import *

_logger = load_logger("generator")
_logger.info("generator initialized")



def run_build(app_label: str, output_dir=None, templates_dir="templates", silent=False):
    """Generate dashboards, views, and urls for a Django app."""
    try:
        apps.get_app_config(app_label)
    except LookupError:
        print(f"❌ App '{app_label}' not found in INSTALLED_APPS.")
        sys.exit(1)

    app_module = importlib.import_module(app_label)
    base_dir = Path(app_module.__file__).resolve().parent
    output_dir = Path(output_dir or base_dir)
    tpl_dir = output_dir / templates_dir / app_label
    tpl_dir.mkdir(parents=True, exist_ok=True)

    print(f"🧩 Generating HyperX components for app: {app_label}\n")

    dashboard_path = tpl_dir / f"dashboard_{app_label}.html"
    views_path = output_dir / f"views_{app_label}.py"
    urls_path = output_dir / f"urls_{app_label}.py"

    generate_dashboard(app_label, output=dashboard_path, silent=silent)
    generate_views(app_label, output=views_path, silent=silent)
    generate_urls(app_label, output=urls_path, silent=silent)

    print("✅ All components generated successfully:")
    print(f"   • Dashboard → {dashboard_path}")
    print(f"   • Views     → {views_path}")
    print(f"   • URLs      → {urls_path}\n")
    print(f"🎯 Add to your main urls.py:")
    print(f"   path('', include('{app_label}.urls_{app_label}'))")


def find_django_settings(start_dir="."):
    """Recursively search for settings.py containing SECRET_KEY."""
    from pathlib import Path
    import os

    for root, dirs, files in os.walk(start_dir):
        if "settings.py" in files:
            settings_path = Path(root) / "settings.py"
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "SECRET_KEY" in content:
                        return settings_path.resolve()
            except Exception:
                continue
    return None


def run_find_settings(start_dir="."):
    """CLI entrypoint: find Django settings.py file."""
    settings_path = find_django_settings(start_dir)
    _logger.info("checking")
    if settings_path:
        print(f"✅ Found Django settings.py at: {settings_path}")
        return str(settings_path)
    else:
        print("❌ No Django settings.py found.")
        return None