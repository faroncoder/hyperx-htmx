#!/usr/bin/env python3
"""
HTMX Core System Initializer
Auto-loads and precompiles HTMX utilities for the Django environment.
"""

import logging, sys

logger = logging.getLogger(__name__)
_ALREADY_INIT = False
HTMX_REGISTRY = {}

def initialize_htmx_core():
    """
    Initialize and pre-compile HTMX core functionality.
    Call this once during Django startup (AppConfig.ready()).
    """
    global _ALREADY_INIT, HTMX_REGISTRY
    if _ALREADY_INIT:
        return HTMX_REGISTRY
    _ALREADY_INIT = True

    # Skip for Celery/Beat workers
    if any(k in sys.argv[0] for k in ("celery", "beat")):
        logger.info("[HTMX] Initialization skipped for Celery/Beat process.")
        return HTMX_REGISTRY

    logger.info("🔧 Initializing HTMX Core System...")

    try:
        # --- Import core utilities ---
        from htmx_core.utils.htmx_response import hx_render
        from htmx_core.utils.htmx_helpers import hx_redirect, hx_trigger
        from htmx_core.utils.htmx_defaults import (
            htmx_defaults, htmx_upload_defaults, htmx_form_defaults,
            htmx_search_defaults, htmx_sidemenu_defaults, htmx_modal_defaults,
            htmx_clean_url_defaults, htmx_xtab_defaults
        )
        from htmx_core.utils.htmx_helpers import (
            is_htmx_request, htmx_login_required, hx_redirect, hx_trigger
        )
        from htmx_core.middleware.htmx_security import HTMXTokenManager
        from htmx_core.mixins.htmx_mixin import (
            HTMXMessageMixin, HTMXRedirectMixin, HTMXLoginRequiredMixin
        )
        from htmx_core.middleware.htmx_benchmark_security import (
            HTMXContentMiddleware, HTMXSecurityMiddleware,
            HTMXErrorMiddleware, HTMXLoadingMiddleware, HTMXBenchmarkMiddleware
        )
        from htmx_core.middleware.htmx_switcher import HTMXRequestSwitcher
        from htmx_core.dispatchers.htmx_dispatcher import HyperXDispatcher
        
        # --- Auto-discovery of additional components ---
        try:
            from htmx_core.utils.htmx_auto_discovery import get_auto_registry
            auto_discovered = get_auto_registry()
            logger.info(f"🔍 Auto-discovered components: {sum(len(comps) for comps in auto_discovered.values())} total")
        except Exception as e:
            logger.warning(f"⚠️ Auto-discovery failed: {e}")
            auto_discovered = {'middleware': {}, 'mixins': {}, 'helpers': {}, 'defaults': {}, 'decorators': {}, 'dispatchers': {}, 'views': {}, 'forms': {}}

        # --- Registry definition (Manual + Auto-discovered) ---
        HTMX_REGISTRY = {
            "dispatchers": {
                "HyperXDispatcher": HyperXDispatcher,
                **auto_discovered.get('dispatchers', {})
            },
            "decorators": {
                "htmx_login_required": htmx_login_required,
                **auto_discovered.get('decorators', {})
            },
            "mixins": {
                "HTMXMessageMixin": HTMXMessageMixin,
                "HTMXRedirectMixin": HTMXRedirectMixin,
                "HTMXLoginRequiredMixin": HTMXLoginRequiredMixin,
                **auto_discovered.get('mixins', {})
            },
            "helpers": {
                "is_htmx_request": is_htmx_request,
                "hx_redirect": hx_redirect,
                "hx_trigger": hx_trigger,
                **auto_discovered.get('helpers', {})
            },
            "defaults": {
                "htmx_defaults": htmx_defaults,
                "htmx_upload_defaults": htmx_upload_defaults,
                "htmx_form_defaults": htmx_form_defaults,
                "htmx_search_defaults": htmx_search_defaults,
                "htmx_sidemenu_defaults": htmx_sidemenu_defaults,
                "htmx_modal_defaults": htmx_modal_defaults,
                "htmx_clean_url_defaults": htmx_clean_url_defaults,
                "htmx_xtab_defaults": htmx_xtab_defaults,
                **auto_discovered.get('defaults', {})
            },
            "middleware": {
                "HTMXRequestSwitcher": HTMXRequestSwitcher,
                "HTMXSecurityMiddleware": HTMXSecurityMiddleware,
                "HTMXContentMiddleware": HTMXContentMiddleware,
                "HTMXErrorMiddleware": HTMXErrorMiddleware,
                "HTMXLoadingMiddleware": HTMXLoadingMiddleware,
                "HTMXBenchmarkMiddleware": HTMXBenchmarkMiddleware,
                **auto_discovered.get('middleware', {})
            },
            "tokens": {"HTMXTokenManager": HTMXTokenManager},
            "views": auto_discovered.get('views', {}),
            "forms": auto_discovered.get('forms', {}),
        }

        # Optionally make global helpers available
        import builtins
        builtins.hx_render = hx_render
        builtins.hx_redirect = hx_redirect
        builtins.hx_trigger = hx_trigger

        logger.info("✅ HTMX Core System initialized successfully")
        logger.info(f"   - {len(HTMX_REGISTRY['middleware'])} middleware classes registered")
        logger.info(f"   - {len(HTMX_REGISTRY['mixins'])} mixins registered")
        logger.info(f"   - {len(HTMX_REGISTRY['helpers'])} helper utilities loaded")

        return HTMX_REGISTRY

    except ImportError as e:
        logger.error(f"❌ Failed to initialize HTMX Core System: {e}")
    except Exception as e:
        logger.exception(f"❌ Unexpected error during HTMX Core initialization: {e}")

    return HTMX_REGISTRY


def get_htmx_registry():
    """Expose the live HTMX registry"""
    return HTMX_REGISTRY


def is_htmx_core_ready():
    """Check if HTMX Core system is initialized"""
    return bool(HTMX_REGISTRY)


# Auto-initialize when imported (not during script runs)
if __name__ != "__main__":
    initialize_htmx_core()
