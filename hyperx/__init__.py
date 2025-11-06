"""
HyperX Package
Framework-agnostic declarative core with optional Django integration.
"""

from importlib import import_module
from pathlib import Path

__version__ = "3.3.0"
__author__ = "Faroncoder"
__license__ = "MIT"

# Core registry containers
ELEMENT_REGISTRY = {}
_LOGGER = None


def get_static_path() -> Path:
    """Return the absolute path to bundled static assets."""
    return Path(__file__).parent / "static" / "hxjs"


def init_logger():
    """Lazy initialize the internal logger."""
    global _LOGGER
    if _LOGGER is None:
        from hyperx.logger.hx_logger import get_logger
        _LOGGER = get_logger("hyperx")
    return _LOGGER


def load_elements():
    """Dynamically import all elements under hyperx/elements/."""
    base = Path(__file__).parent / "elements"
    for f in base.glob("*.py"):
        if f.name.startswith("__"):
            continue
        import_module(f"hyperx.elements.{f.stem}")
    return True


def boot(debug: bool = False):
    """Initialize HyperX runtime (logger + elements)."""
    log = init_logger()
    log.info(f"[HyperX] Booting package version {__version__}")
    load_elements()
    if debug:
        log.debug(f"[HyperX] Static assets at: {get_static_path()}")
    return True
