import importlib
import pkgutil
import logging

_logger = logging.getLogger("hyperx")

__all__ = []

for module in pkgutil.iter_modules(__path__):
    try:
        importlib.import_module(f"{__name__}.{module.name}")
        __all__.append(module.name)
        _logger.debug(f"[HyperX Elements] Loaded: {module.name}")
    except Exception as e:
        _logger.warning(f"[HyperX Elements] Failed to load {module.name}: {e}")

_logger.info(f"[HyperX Elements] {len(__all__)} modules registered → {__all__}")
