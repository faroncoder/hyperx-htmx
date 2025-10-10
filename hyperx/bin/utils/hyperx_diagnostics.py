import platform, os
from django.conf import settings
import platform, os
import subprocess

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
    print("🔍 Checking HyperX installation...")
    apps = getattr(settings, 'INSTALLED_APPS', [])
    if 'hyperx' not in apps:
        print("❌ hyperx not in INSTALLED_APPS")
    else:
        print("✅ hyperx registered")

    middlewares = getattr(settings, "MIDDLEWARE", [])
    required = [
        'django_htmx.middleware.HtmxMiddleware',
        'hyperx.middleware.middleware.HyperXMiddleware',
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



def check_hyperx(args=None):
    import logging
    report = {}

    try:
        import hyperx
        report["core"] = True
        print("✅ Core module imported successfully.")
    except Exception as e:
        report["core"] = False
        print(f"❌ Failed to import HyperX core: {e}")

    middlewares = getattr(settings, "MIDDLEWARE", [])
    has_main = any("hyperx.middleware.HyperXMiddleware" in m for m in middlewares)
    has_security = any("hyperx.middleware.HyperXSecurityMiddleware" in m for m in middlewares)

    if has_main:
        print("✅ HyperXMiddleware is active.")
    else:
        print("⚠️ HyperXMiddleware not found in MIDDLEWARE.")

    if has_security:
        print("✅ Security middleware is active.")
    else:
        print("⚠️ HyperXSecurityMiddleware not found in MIDDLEWARE.")

    report["middleware"] = has_main and has_security

    try:
        from hyperx.templatetags.hyperx import TAG_CONVERTERS
        count = len(TAG_CONVERTERS)
        print(f"✅ {count} declarative <hx:*> tags loaded.")
        report["tags"] = True
    except Exception as e:
        print(f"❌ Failed to load template tags: {e}")
        report["tags"] = False

    try:
        import hyperx
        ai_enabled = getattr(hyperx, "AI_TOOLS_AVAILABLE", False)
        watcher_enabled = getattr(hyperx, "WATCHER_AVAILABLE", False)

        ai_status = "✅ Enabled" if ai_enabled else "⚠️ Not available"
        watcher_status = "✅ Enabled" if watcher_enabled else "⚠️ Not available"

        print(f"🧠 AI Schema Autogen: {ai_status}")
        print(f"👁️ Dataset Watcher: {watcher_status}")
    except Exception as e:
        print(f"❌ Failed to check optional integrations: {e}")

    passed = all(report.values())
    print("\n" + "─" * 50)
    if passed:
        print("🎉 All HyperX components operational!")
    else:
        print("⚠️ Some checks failed. See messages above.")
    print("─" * 50 + "\n")

    # Optional: log diagnostics
    logging.getLogger("hyperx").info(f"[CheckHyperX] Summary: {report}")
    




def tail_journalctl(unit: str, lines: int = 20) -> str:
    """Fetch the last N lines of a systemd service log."""
    try:
        return subprocess.getoutput(f"journalctl -u {unit} -n {lines} --no-pager")
    except Exception:
        return "(⚠️ journalctl not available or insufficient permissions)"

def watcher_status(unit="hyperx-dataset-watch.service") -> str:
    """Return status emoji + state string."""
    try:
        status = subprocess.getoutput(f"systemctl is-active {unit}").strip()
        return {
            "active": "🟢 ACTIVE",
            "inactive": "⚪ INACTIVE",
            "failed": "🔴 FAILED"
        }.get(status, f"⚠️ {status.upper()}")
    except Exception:
        return "❓ UNKNOWN"
