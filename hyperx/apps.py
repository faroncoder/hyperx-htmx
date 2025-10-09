# hyperx/apps.py
from django.apps import AppConfig
from django.conf import settings
import logging
import sys

class HyperXConfig(AppConfig):
    name = "hyperx"
    label = "hyperx"
    verbose_name = "HyperX – HTMX Sidekick"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        """
        Runs once when Django app registry is ready.
        Safely loads HyperX's compiler & tags without circular imports.
        """
        self.logger = logging.getLogger("hyperx")

        # Skip autodiscover in management commands that don't need runtime loading
        if any(cmd in sys.argv for cmd in ("makemigrations", "migrate", "collectstatic", "shell")):
            self.logger.debug("[HyperX] Skipping autodiscover during management command.")
            return

        try:
            # Perform lazy import to avoid circular load during Django startup
            # from importlib import import_module
            from hyperx.autodiscover import autodiscover
            autodiscover()
            self.logger.info("⚡ HyperX autodiscover() executed successfully.")
        except ModuleNotFoundError:
            self.logger.warning("[HyperX] autodiscover module not found; skipping optional discovery.")
        except Exception as e:
            self.logger.exception(f"❌ HyperX AppConfig startup error: {e}")

        # Optional: show runtime context for developers
        if getattr(settings, "DEBUG", False):
            self.logger.info("[HyperX] DEBUG mode detected — runtime helpers will auto-inject.")
