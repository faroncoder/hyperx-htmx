import sys
from pathlib import Path
from django.apps import apps
import importlib
from hyperx.bin.generator.htmx_backend_dashboard import generate_dashboard
from hyperx.bin.generator.htmx_backend_views import generate_views
from hyperx.bin.generator.htmx_backend_urls import generate_urls

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
