import importlib, pkgutil, logging

_logger = logging.getLogger("hyperx")

def autodiscover():
    """
    Dynamically import all modules under hyperx/templatetags/
    and hyperx/extensions/ if they exist.
    """
    base_packages = ["hyperx.templatetags", "hyperx.extensions"]
    for base in base_packages:
        try:
            pkg = importlib.import_module(base)
        except ModuleNotFoundError:
            continue
        for mod in pkgutil.iter_modules(pkg.__path__):
            try:
                importlib.import_module(f"{base}.{mod.name}")
                _logger.debug(f"[HyperX autodiscover] Imported {base}.{mod.name}")
            except Exception as e:
                _logger.warning(f"[HyperX autodiscover] Failed {base}.{mod.name}: {e}")
