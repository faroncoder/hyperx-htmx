from django import template
from django.utils.html import escape
import importlib, pkgutil, logging
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from hyperx.bin.cli.logger.hx_logger import load_logger
from hyperx.core.hx.library_loader import *
from django.template.library import Library


# ensure the real /hyperx path is importable
real_root = Path("/hyperx")
if str(real_root) not in sys.path:
    sys.path.insert(0, str(real_root))


register = Library()
_logger = load_logger("hx-autodiscover")
_logger.info("hx-autodiscover initialized")


def autodiscover(path=None, base_packages=None):
    """
    Dynamically import all modules under the given base packages.
    """
    if not path:
        path = Path(__file__).resolve().parent.parent.parent

    # Default packages to scan
    if not base_packages:
        base_packages = [
            "hyperx.templatetags",
            "hyperx.templatetags.hyperx_elements", 
            "hyperx.core.hx",
        ]
        _logger.info(f"[HyperX autodiscover] No base packages provided, using defaults: {base_packages}")

    elif isinstance(base_packages, str):
        base_packages = [base_packages]

    # --- scan loop (always runs) ---
    for base in base_packages:
        try:
            pkg = importlib.import_module(base)
            _logger.debug(f"[HyperX autodiscover] Scanning {base}...")
        except ModuleNotFoundError:
            _logger.warning(f"[HyperX autodiscover] Module not found: {base}")
            continue

        if hasattr(pkg, "__path__"):
            for mod in pkgutil.iter_modules(pkg.__path__):
                # Skip private or disabled modules starting with '_'
                if mod.name.startswith("_"):
                    _logger.debug(f"[HyperX autodiscover] Skipped {base}.{mod.name} (prefixed with _)") 
                    continue
                try:
                    importlib.import_module(f"{base}.{mod.name}")
                    _logger.debug(f"[HyperX autodiscover] Imported {base}.{mod.name}")
                except Exception as e:
                    _logger.warning(f"[HyperX autodiscover] Failed {base}.{mod.name}: {e}")