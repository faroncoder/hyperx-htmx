from hyperx.logger.hx_logger import load_logger
from hyperx.loader.element_loader import load_elements
from hyperx.loader.library_loader import load_config, register_libraries
from pathlib import Path
import os, sys, django

_logger = load_logger("hx_loader")
_logger.info("hx_loader initialized")

def initialize(debug=False):
    _logger.info("[HyperX] Boot sequence starting...")

    # 1️⃣  Load all element modules
    count = load_elements()
    _logger.info(f"[HyperX] {count} elements loaded.")

    # 2️⃣  Read YAML config (delegated to library_loader)
    config_path = Path(__file__).parent / "hyperx_config.yaml"
    libs = load_config(config_path)
    if libs:
        register_libraries(libs)
        _logger.info("[HyperX] Template libraries registered.")
    else:
        _logger.warning("[HyperX] No libraries found in config.")

    _logger.info("🚀  HyperX runtime initialized successfully.")
    if debug:
        _logger.debug("Debug mode active.")
    return True


if __name__ == "__main__":
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        _logger.warning("[HyperX] No DJANGO_SETTINGS_MODULE set; running standalone.")
    else:
        try:
            django.setup()
        except Exception as e:
            _logger.warning(f"[HyperX] Django setup failed: {e}")

    initialize(debug=True)


def init_hx():
    """
    Initialize the HX runtime (called automatically by bs_loader).

    This stub is where you’d eventually wire in HX-specific tasks such as:
      • registering HTMX/TabX processors
      • attaching runtime compilers
      • verifying middleware availability
      • pre-warming any HX caches
    """
    try:
        _logger.info("[HXLoader] ✅ HX runtime initialized.")
        return True
    except Exception as e:
        _logger.error(f"[HXLoader] HX runtime initialization failed: {e}", exc_info=True)
        return False
