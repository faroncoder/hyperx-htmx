"""
checkhyperx.py
────────────────────────────────────────────
Django management command to verify HyperX installation.
Run:
    python manage.py checkhyperx
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import importlib
import logging

class Command(BaseCommand):
    help = "Verify HyperX integration and environment setup."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 HyperX Diagnostic Utility\n"))

        report = {}

        # ─────────────────────────────
        # 1️⃣  Core Import Verification
        # ─────────────────────────────
        try:
            import hyperx
            report["core"] = True
            self.stdout.write(self.style.SUCCESS("✅ Core module imported successfully."))
        except Exception as e:
            report["core"] = False
            self.stdout.write(self.style.ERROR(f"❌ Failed to import HyperX core: {e}"))

        # ─────────────────────────────
        # 2️⃣  Middleware Check
        # ─────────────────────────────
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

        # ─────────────────────────────
        # 3️⃣  Template Tag + Element Check
        # ─────────────────────────────
        try:
            from hyperx.templatetags.hyperx import TAG_CONVERTERS
            count = len(TAG_CONVERTERS)
            self.stdout.write(self.style.SUCCESS(f"✅ {count} declarative <hx:*> tags loaded."))
            report["tags"] = True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to load template tags: {e}"))
            report["tags"] = False

        # ─────────────────────────────
        # 4️⃣  AI & Dataset Integration
        # ─────────────────────────────
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

        # ─────────────────────────────
        # 5️⃣  Final Summary
        # ─────────────────────────────
        passed = all(report.values())
        self.stdout.write("\n" + "─" * 50)
        if passed:
            self.stdout.write(self.style.SUCCESS("🎉 All HyperX components operational!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Some checks failed. See messages above."))
        self.stdout.write("─" * 50 + "\n")

        # Optional: log diagnostics
        logging.getLogger("hyperx").info(f"[CheckHyperX] Summary: {report}")


