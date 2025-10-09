import platform, os
from django.conf import settings
from django.conf import settings
import platform, os


def core_info():
    return {
        "system": platform.system(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
        "apps": getattr(settings, "INSTALLED_APPS", []),
        "middleware": getattr(settings, "MIDDLEWARE", []),
    }




def run_check(verbose=False):
    """Run HyperX installation check and configuration validation."""
    print("🔍 Checking HyperX installation...\n")
    apps = getattr(settings, 'INSTALLED_APPS', [])
    if 'hyperx' not in apps:
        print("❌ hyperx not in INSTALLED_APPS")
    else:
        print("✅ hyperx registered")

    middlewares = getattr(settings, "MIDDLEWARE", [])
    required = [
        'django_htmx.middleware.HtmxMiddleware',
        'hyperx.middleware.HyperXMiddleware',
    ]
    for mw in required:
        print("✅" if mw in middlewares else "❌", mw)




def run_audit(json_path=None):
    """Generate environment and system audit."""
    data = {
        "system": platform.system(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
    }
    for k, v in data.items():
        print(f"{k:<10}: {v}")
    if json_path:
        import json
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Audit saved → {json_path}")



 def check_hyperx():
    try:
        import hyperx
        report["core"] = True
        self.stdout.write(self.style.SUCCESS("✅ Core module imported successfully."))
    except Exception as e:
        report["core"] = False
        self.stdout.write(self.style.ERROR(f"❌ Failed to import HyperX core: {e}"))

    middlewares = getattr(settings, "MIDDLEWARE", [])
    has_main = any("hyperx.middleware.HyperXMiddleware" in m for m in middlewares)
    has_security = any("hyperx.middleware.HyperXSecurityMiddleware" in m for m in middlewares)

    if has_main:
        self.stdout.write(self.style.SUCCESS("✅ HyperXMiddleware is active."))
    else:
        self.stdout.write(self.style.WARNING("⚠️ HyperXMiddleware not found in MIDDLEWARE."))

    if has_security:
        self.stdout.write(self.style.SUCCESS("✅ Security middleware is active."))
    else:
        self.stdout.write(self.style.WARNING("⚠️ HyperXSecurityMiddleware not found in MIDDLEWARE."))

    report["middleware"] = has_main and has_security


    try:
        from hyperx.templatetags.hyperx import TAG_CONVERTERS
        count = len(TAG_CONVERTERS)
        self.stdout.write(self.style.SUCCESS(f"✅ {count} declarative <hx:*> tags loaded."))
        report["tags"] = True
    except Exception as e:
        self.stdout.write(self.style.ERROR(f"❌ Failed to load template tags: {e}"))
        report["tags"] = False

    try:
        import hyperx
        ai_enabled = getattr(hyperx, "AI_TOOLS_AVAILABLE", False)
        watcher_enabled = getattr(hyperx, "WATCHER_AVAILABLE", False)

        ai_status = "✅ Enabled" if ai_enabled else "⚠️ Not available"
        watcher_status = "✅ Enabled" if watcher_enabled else "⚠️ Not available"

        self.stdout.write(self.style.SUCCESS(f"🧠 AI Schema Autogen: {ai_status}"))
        self.stdout.write(self.style.SUCCESS(f"👁️ Dataset Watcher: {watcher_status}"))
    except Exception as e:
        self.stdout.write(self.style.ERROR(f"❌ Failed to check optional integrations: {e}"))


    passed = all(report.values())
    self.stdout.write("\n" + "─" * 50)
    if passed:
        self.stdout.write(self.style.SUCCESS("🎉 All HyperX components operational!"))
    else:
        self.stdout.write(self.style.WARNING("⚠️ Some checks failed. See messages above."))
    self.stdout.write("─" * 50 + "\n")

    # Optional: log diagnostics
    logging.getLogger("hyperx").info(f"[CheckHyperX] Summary: {report}")
    

def run_check(verbose=False):
    """Run HyperX installation check and configuration validation."""
    print("🔍 Checking HyperX installation...\n")
    apps = getattr(settings, 'INSTALLED_APPS', [])
    if 'hyperx' not in apps:
        print("❌ hyperx not in INSTALLED_APPS")
    else:
        print("✅ hyperx registered")

    middlewares = getattr(settings, "MIDDLEWARE", [])
    required = [
        'django_htmx.middleware.HtmxMiddleware',
        'hyperx.middleware.HyperXMiddleware',
    ]
    for mw in required:
        print("✅" if mw in middlewares else "❌", mw)




def run_audit(json_path=None):
    """Generate environment and system audit."""
    data = {
        "system": platform.system(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
    }
    for k, v in data.items():
        print(f"{k:<10}: {v}")
    if json_path:
        import json
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Audit saved → {json_path}")


    try:
        import hyperx
        report["core"] = True
        self.stdout.write(self.style.SUCCESS("✅ Core module imported successfully."))
    except Exception as e:
        report["core"] = False
        self.stdout.write(self.style.ERROR(f"❌ Failed to import HyperX core: {e}"))


    middlewares = getattr(settings, "MIDDLEWARE", [])
    has_main = any("hyperx.middleware.HyperXMiddleware" in m for m in middlewares)
    has_security = any("hyperx.middleware.HyperXSecurityMiddleware" in m for m in middlewares)

    if has_main:
        self.stdout.write(self.style.SUCCESS("✅ HyperXMiddleware is active."))
    else:
        self.stdout.write(self.style.WARNING("⚠️ HyperXMiddleware not found in MIDDLEWARE."))

    if has_security:
        self.stdout.write(self.style.SUCCESS("✅ Security middleware is active."))
    else:
        self.stdout.write(self.style.WARNING("⚠️ HyperXSecurityMiddleware not found in MIDDLEWARE."))

    report["middleware"] = has_main and has_security



    try:
        from hyperx.templatetags.hyperx import TAG_CONVERTERS
        count = len(TAG_CONVERTERS)
        self.stdout.write(self.style.SUCCESS(f"✅ {count} declarative <hx:*> tags loaded."))
        report["tags"] = True
    except Exception as e:
        self.stdout.write(self.style.ERROR(f"❌ Failed to load template tags: {e}"))
        report["tags"] = False


    try:
        import hyperx
        ai_enabled = getattr(hyperx, "AI_TOOLS_AVAILABLE", False)
        watcher_enabled = getattr(hyperx, "WATCHER_AVAILABLE", False)

        ai_status = "✅ Enabled" if ai_enabled else "⚠️ Not available"
        watcher_status = "✅ Enabled" if watcher_enabled else "⚠️ Not available"

        self.stdout.write(self.style.SUCCESS(f"🧠 AI Schema Autogen: {ai_status}"))
        self.stdout.write(self.style.SUCCESS(f"👁️ Dataset Watcher: {watcher_status}"))
    except Exception as e:
        self.stdout.write(self.style.ERROR(f"❌ Failed to check optional integrations: {e}"))


    passed = all(report.values())
    self.stdout.write("\n" + "─" * 50)
    if passed:
        self.stdout.write(self.style.SUCCESS("🎉 All HyperX components operational!"))
    else:
        self.stdout.write(self.style.WARNING("⚠️ Some checks failed. See messages above."))
    self.stdout.write("─" * 50 + "\n")

    # Optional: log diagnostics
    logging.getLogger("hyperx").info(f"[CheckHyperX] Summary: {report}")
