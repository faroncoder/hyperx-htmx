import logging, os, sys
from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class HTMXCoreConfig(AppConfig):
    name = "htmx_core"
    verbose_name = "HTMX Core System"

    def ready(self):
        """Boot sequence + middleware registration + default prefix and settings"""
        try:
            from htmx_core.initializer import initialize_htmx_core
            initialize_htmx_core()

            self.ensure_htmx_prefix()
            self.ensure_default_settings()
            self.ensure_middleware_order()

            # Developer-mode boot diagnostics
            if getattr(settings, "DEBUG", False) or os.getenv("ENABLE_HTMX_CORE_BOOT", "1") == "1":
                try:
                    from htmx_core.views.htmx_views import htmx_response
                    import builtins
                    builtins.htmx_response = htmx_response
                except ImportError as e:
                    logger.warning(f"[htmx_core] Could not import htmx_response: {e}")
                # self.build_tab_mapping_on_boot()
                logger.info("✅ HTMX Core fully initialized and synchronized with client.")
        except Exception as e:
            logger.error(f"[htmx_core] Failed to initialize HTMX Core: {e}")
            # Don't raise the exception to prevent Django startup failure
            # Instead, log the error and continue

    # ------------------------------------------------------------------ #
    #  Cache prefix
    # ------------------------------------------------------------------ #
    def ensure_htmx_prefix(self):
        try:
            project_slug = getattr(settings, "PROJECT_SLUG", os.getenv("PROJECT_SLUG", "hyperx"))
            environment = getattr(settings, "ENVIRONMENT_NAME", os.getenv("ENVIRONMENT_NAME", "local"))
            prefix = f"{project_slug}:{environment}:htmx:"

            if not hasattr(settings, "HTMX_CACHE_PREFIX"):
                setattr(settings, "HTMX_CACHE_PREFIX", prefix)
                logger.info(f"[htmx_core] HTMX_CACHE_PREFIX initialized → {prefix}")

            try:
                test_key = f"{prefix}bootcheck"
                cache.set(test_key, "ok", 5)
                if cache.get(test_key) == "ok":
                    logger.debug("[htmx_core] Cache connection verified ✅")
            except Exception as e:
                logger.warning(f"[htmx_core] Cache test failed: {e}")
        except Exception as e:
            logger.error(f"[htmx_core] Failed to set HTMX cache prefix: {e}")

    # ------------------------------------------------------------------ #
    #  Default fallback settings
    # ------------------------------------------------------------------ #
    def ensure_default_settings(self):
        defaults = {
            # "HTMX_PROTECTED_ENDPOINTS": [r"^/htmx/"],
            # "HTMX_REDIRECT_AUTH": "/dashboard/",
            # "HTMX_REDIRECT_ANON": "/login/",
            # "HTMX_BENCHMARK_ENABLED": False,
        }
        for key, value in defaults.items():
            if not hasattr(settings, key):
                setattr(settings, key, value)
                logger.debug(f"[htmx_core] Default setting applied: {key}")

    # ------------------------------------------------------------------ #
    #  Middleware stack validation
    # ------------------------------------------------------------------ #
    def ensure_middleware_order(self):
        """
        Ensure new HTMX middleware stack is active and ordered correctly.
        Includes updated security and benchmark components.
        """
        try:
            required = [
                # 1️⃣ Classify and contextualize
                "htmx_core.middleware.htmx_switcher.HTMXRequestSwitcher",
                # 2️⃣ Enforce access control and protect endpoints
                "htmx_core.middleware.htmx_benchmark_security.HTMXSecurityMiddleware",
                # 3️⃣ Content auto-clear / reinitialization wrapper
                "htmx_core.middleware.htmx_benchmark_security.HTMXContentMiddleware",
                # 4️⃣ Graceful HTMX error recovery (alerts)
                "htmx_core.middleware.htmx_benchmark_security.HTMXErrorMiddleware",
                # 5️⃣ Optional: add client-side loader CSS (redundant if JS overlay used)
                # "htmx_core.middleware.htmx_benchmark_security.HTMXLoadingMiddleware",
                # 6️⃣ Optional analytics layer - HTMXBenchmarkMiddleware not available
                # "htmx_core.middleware.htmx_benchmark_security.HTMXBenchmarkMiddleware",
            ]

            current = list(getattr(settings, "MIDDLEWARE", []))
            added = False
            for mw in required:
                if mw not in current:
                    current.append(mw)
                    added = True
                    logger.debug(f"[htmx_core] Added middleware: {mw}")

            if added:
                settings.MIDDLEWARE = current
                logger.info("✅ HTMX middleware stack verified and updated.")
        except Exception as e:
            logger.error(f"[htmx_core] Failed to configure middleware: {e}")

    # # ------------------------------------------------------------------ #
    # #  Dynamic tab mapping (client-to-server registry)
    # # ------------------------------------------------------------------ #
    # def build_tab_mapping_on_boot(self):
    #     try:
    #         from htmx_core.views.tab_reflector import build_tab_mapping
    #         logger.info("=" * 60)
    #         logger.info("🔥  HTMX Core Boot Sequence")
    #         logger.info("⏳  Building dynamic tab mapping at startup...")

    #         mapping = build_tab_mapping()
    #         cache.set("dynamic_tab_mapping", mapping, None)
    #         sys.modules["htmx_core.views.tab_reflector"]._TAB_MAPPING = mapping

    #         logger.info(f"✅  Tab mapping built ({len(mapping)} entries)")
    #         logger.info("=" * 60)
    #     except Exception as e:
    #         logger.warning("HTMX Core boot sequence failed: %s", e)
