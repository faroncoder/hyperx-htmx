import platform, os
from django.conf import settings
import platform, os
import subprocess
from hyperx.bin.utils.hx_logger import loadselflogger, log_functions
_logger = loadselflogger('hx-coreinfo')
_log_functions = log_functions


def core_info():
    coreinfo = {
        "system": platform.system(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
        "apps": getattr(settings, "INSTALLED_APPS", []),
        "middleware": getattr(settings, "MIDDLEWARE", []),
    }
    _logger.info(f"Core info: {coreinfo}")
    return coreinfo
   

   
def _run_core_info(verbose=True):
    """Run HyperX installation check and configuration validation."""
    log_event("_run_core_info", locals(), {})
    apps = getattr(settings, 'INSTALLED_APPS', [])
    if 'hyperx' not in apps:
        _logger.warning("❌ hyperx not in INSTALLED_APPS")
    else:
        _logger.info("✅ hyperx registered")

    middlewares = getattr(settings, "MIDDLEWARE", [])
    required = [
        'django_htmx.middleware.HtmxMiddleware',
        'hyperx.middleware.middleware.HyperXMiddleware',
    ]
    for mw in required:
        _logger.info("✅" if mw in middlewares else "❌", mw)
        has_main = 'hyperx.middleware.middleware.HyperXMiddleware' in middlewares
        has_security = 'django.middleware.security.SecurityMiddleware' in middlewares   
        return has_main and has_security

