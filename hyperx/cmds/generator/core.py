#!/usr/bin/env python3
"""
HyperX Generator Core
──────────────────────────────────────────────
Auto-generates HTMX dashboards, views, and URLs
for any Django app and ensures HyperX integration.
"""

import os, re, importlib, django
from pathlib import Path
from django.apps import apps
from hyperx.logger.hx_logger import load_logger
from hyperx.cmds.generator.htmx_backend_dashboard import generate_dashboard
from hyperx.cmds.generator.htmx_backend_views import generate_views
from hyperx.cmds.generator.htmx_backend_urls import generate_urls

_logger = load_logger("generator")
_logger.info("generator initialized")

# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────

def find_django_settings(start=".") -> Path | None:
    """Locate the first settings.py file starting from the given directory."""
    for root, _, files in os.walk(start):
        if "settings.py" in files:
            return Path(root) / "settings.py"
    return None


def insert_if_missing(block: str, item: str, marker: str):
    """Insert a line into a Django settings list (INSTALLED_APPS or MIDDLEWARE) if missing."""
    # Normalize: remove quotes for matching safety
    normalized = item.strip("'\"")
    pattern = rf"['\"]{re.escape(normalized)}['\"]"
    if not re.search(pattern, block):
        block = re.sub(rf"({marker}\s*=\s*\[)", rf"\1\n    {item},", block)
        return block, True
    return block, False



def info(msg: str, silent=False):
    """Print messages unless in silent mode."""
    if not silent:
        print(msg)


# ─────────────────────────────────────────────
# Ensure HyperX integration in settings.py
# ─────────────────────────────────────────────

def ensure_hyperx_in_settings(settings_path: Path, app_label: str, silent=False):
    """Ensure required HyperX apps, middleware, and configs exist in settings.py."""
    text = settings_path.read_text()
    changed = False

    required_apps = [f"'{app_label}'", "'django_htmx'", "'hyperx'"]
    required_mw = [
        '"django_htmx.middleware.HtmxMiddleware"',
        '"hyperx.middleware.middleware.HyperXMiddleware"',
        '"hyperx.middleware.middleware.HyperXSecurityMiddleware"',
    ]

    # INSTALLED_APPS
    if "INSTALLED_APPS" in text:
        for app in required_apps:
            text, inserted = insert_if_missing(text, app, "INSTALLED_APPS")
            if inserted:
                info(f"✅ Added {app} to INSTALLED_APPS", silent)
                changed = True
    else:
        info("⚠️  Could not locate INSTALLED_APPS block in settings.py", silent)

    # MIDDLEWARE
    if "MIDDLEWARE" in text:
        for mw in required_mw:
            text, inserted = insert_if_missing(text, mw, "MIDDLEWARE")
            if inserted:
                info(f"✅ Added {mw} to MIDDLEWARE", silent)
                changed = True
    else:
        info("⚠️  Could not locate MIDDLEWARE block in settings.py", silent)

    # Configuration block
    if "HYPERX_MIDDLEWARE" not in text:
        text += """

# ==========================================
# HyperX Configuration (auto-added)
# ==========================================
HYPERX_MIDDLEWARE = {
    'AUTO_VALIDATE_HTMX': True,
    'AUTO_PARSE_XTAB': True,
    'SECURITY_LOGGING': True,
    'PERFORMANCE_TRACKING': True,
    'STRICT_XTAB_VALIDATION': False,
}

HYPERX_SECURITY = {
    'RATE_LIMITING': True,
    'PATTERN_DETECTION': True,
    'AUTO_BLOCKING': False,
    'MAX_REQUESTS_PER_MINUTE': 60,
}
"""
        info("✅ Added HyperX configuration block", silent)
        changed = True

    if changed:
        settings_path.write_text(text)
        info(f"✨ Updated settings.py → {settings_path}", silent)
    else:
        info("ℹ️  No changes required in settings.py", silent)


def create_django_app(app_label: str, base_dir=Path.cwd(), silent=False):
    """Auto-create a basic Django app if it doesn’t exist."""
    app_path = base_dir / app_label
    if not app_path.exists():
        (app_path / "templates" / app_label).mkdir(parents=True)
        for filename in ["__init__.py", "views.py", "models.py", "urls.py"]:
            (app_path / filename).touch()
        info(f"🆕 Created new Django app: {app_label}", silent)


# ─────────────────────────────────────────────
# Main generator entrypoint
# ─────────────────────────────────────────────
def run_build(app_label: str, output_dir=None, templates_dir="templates", silent=False):
    """Generate dashboards, views, and URLs for a Django app."""

    # 1️⃣ Locate settings.py and ensure DJANGO_SETTINGS_MODULE
    settings_path = find_django_settings()
    if not settings_path:
        info("❌ Could not locate settings.py — please run from a Django project root.", silent)
        return

    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        settings_module = (
            f"{settings_path.parent.name}.settings"
            if (settings_path.parent / "__init__.py").exists()
            else "settings"
        )
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        info(f"⚙️  Using settings module → {settings_module}", silent)

    # 2️⃣ Ensure app folder exists on disk BEFORE setup
    app_path = Path.cwd() / app_label
    if not app_path.exists():
        info(f"🆕 Creating Django app folder '{app_label}' before setup.", silent)
        create_django_app(app_label, Path.cwd(), silent)

    # 3️⃣ Ensure app is in INSTALLED_APPS and setup Django
    ensure_hyperx_in_settings(settings_path, app_label, silent)

    import sys, importlib, django
    for mod in ("django.conf", "django.conf.global_settings"):
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    django.setup()
    info("⚙️  Django environment initialized successfully.", silent)


    # 2️⃣ Ensure app exists in INSTALLED_APPS
    try:
        apps.get_app_config(app_label)
        info(f"✅ Found existing app '{app_label}' in INSTALLED_APPS", silent)
    except LookupError:
        info(f"⚠️  App '{app_label}' not found — adding automatically.", silent)
        settings_path = find_django_settings()
        if settings_path:
            ensure_hyperx_in_settings(settings_path, app_label, silent)
            create_django_app(app_label, Path.cwd(), silent)
            django.setup()
            info(f"✅ Added '{app_label}' to INSTALLED_APPS and reloaded Django.", silent)
        else:
            info("❌ Could not locate settings.py to update INSTALLED_APPS.", silent)
            return

    # 3️⃣ Import and prepare paths
    try:
        app_module = importlib.import_module(app_label)
    except ModuleNotFoundError:
        info(f"❌ Could not import app '{app_label}'. Ensure it exists or create it.", silent)
        return

    base_dir = Path(app_module.__file__).resolve().parent
    output_dir = Path(output_dir or base_dir)
    tpl_dir = output_dir / templates_dir / app_label
    tpl_dir.mkdir(parents=True, exist_ok=True)

    info(f"🧩 Generating HyperX components for app: {app_label}\n", silent)

    dashboard_path = tpl_dir / f"dashboard_{app_label}.html"
    views_path = output_dir / f"views_{app_label}.py"
    urls_path = output_dir / f"urls_{app_label}.py"

    # 4️⃣ Generate components
    generate_dashboard(app_label, output=dashboard_path, silent=silent)
    generate_views(app_label, output=views_path, silent=silent)
    generate_urls(app_label, output=urls_path, silent=silent)

    # 5️⃣ Summary
    info("\n╔═══════════════════════════════════════╗", silent)
    info(f"║  ✅ HyperX Build Complete for '{app_label}'  ║", silent)
    info("╚═══════════════════════════════════════╝", silent)
    info(f"📄 Dashboard → {dashboard_path}", silent)
    info(f"🧠 Views     → {views_path}", silent)
    info(f"🌐 URLs      → {urls_path}\n", silent)
    info(f"🔗 Add to your main urls.py:", silent)
    info(f"   path('', include('{app_label}.urls_{app_label}'))\n", silent)

    _logger.info(f"✅ HyperX build complete for '{app_label}'")


# ─────────────────────────────────────────────
# CLI Entrypoint
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m hyperx.cmds.generator.core <app_name>")
        sys.exit(1)
    app_name = sys.argv[1].strip()
    run_build(app_name)
