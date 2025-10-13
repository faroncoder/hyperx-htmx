from django.apps import AppConfig
from django.conf import settings
import logging, sys
from pathlib import Path

class HyperXConfig(AppConfig):
    name = "hyperx"
    label = "hyperx"
    verbose_name = "HyperX – HTMX Sidekick"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        """Runs once when Django app registry is ready."""
        self.logger = logging.getLogger("hyperx")

        # ─────────────────────────────────────────────
        # Skip mgmt commands
        # ─────────────────────────────────────────────
        if any(cmd in sys.argv for cmd in ("makemigrations", "migrate", "collectstatic", "shell")):
            self.logger.debug("[HyperX] Skipping runtime load during management command.")
            return

        # ─────────────────────────────────────────────
        # Autodiscover
        # ─────────────────────────────────────────────
        try:
            from hyperx.autodiscover import autodiscover
            autodiscover()
            self.logger.info("⚡ HyperX autodiscover() executed successfully.")
        except ModuleNotFoundError:
            self.logger.warning("[HyperX] autodiscover module not found; skipping optional discovery.")
        except Exception as e:
            self.logger.exception(f"❌ HyperX AppConfig startup error: {e}")

        # ─────────────────────────────────────────────
        # Check structure: bin and lib
        # ─────────────────────────────────────────────
        root_path = Path(__file__).resolve().parent
        bin_path = root_path / "bin"
        lib_path = root_path / "lib"

        if not bin_path.exists():
            self.logger.warning(f"[HyperX] Missing bin directory: {bin_path}")
        else:
            self.logger.debug(f"[HyperX] Found bin directory: {bin_path}")

        if not lib_path.exists():
            self.logger.warning(f"[HyperX] Missing lib directory: {lib_path}")
        else:
            self.logger.debug(f"[HyperX] Found lib directory: {lib_path}")

        if getattr(settings, "DEBUG", False):
            self.logger.info("[HyperX] DEBUG mode detected — runtime helpers will auto-inject.")
