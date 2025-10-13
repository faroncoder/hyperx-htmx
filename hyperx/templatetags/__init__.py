# hyperx/templatetags/__init__.py
import importlib, pkgutil

for _, modname, _ in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{modname}")
