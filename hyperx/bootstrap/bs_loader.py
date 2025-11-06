#!/usr/bin/env python3
"""
hyperx/bootstrap/bs_loader.py
──────────────────────────────────────────────
Unified bootstrap loader for the HyperX runtime.

Orchestrates:
  1. Logger bootstrap
  2. Element Loader
  3. Library Loader
  4. HX / CX / JSX runtime initializers

MIT License © 2025 Faron
"""

import os
from pathlib import Path
from importlib import import_module
from hyperx.logger.bootstrap_logger import bootstrap_logger
from hyperx.logger.hx_logger import load_logger
from hyperx.loader.hx_loader import init_hx

_logger = load_logger("hyperx.bootstrap.bs_loader")
_logger.info("hyperx.bootstrap.bs_loader initialized")

# ─────────────────────────────────────────────
# 1️⃣  Main initialize() entrypoint
# ─────────────────────────────────────────────
def initialize(debug: bool = False):
    """Boot the full HyperX runtime stack."""
    _logger.info("[Bootstrap] Starting HyperX loader sequence...")

    # 1. Logger bootstrap
    try:
        bootstrap_logger()
        _logger.debug("[Bootstrap] Logger bootstrap complete.")
    except Exception as e:
        _logger.warning(f"[Bootstrap] Logger bootstrap failed: {e}")

    # 2. Element loader
    try:
        from hyperx.loader.element_loader import load_elements
        count = load_elements()
        _logger.info(f"[Bootstrap] ✅ Element loader initialized ({count} elements discovered).")
    except Exception as e:
        _logger.warning(f"[Bootstrap] Element loader failed: {e}")

    # 3. Template library loader
    try:
        from hyperx.loader.library_loader import load_config, register_libraries
        config_path = Path(os.getenv("HYPERX_LIB_CONFIG", Path(__file__).parent.parent / "loader" / "hyperx_config.yaml"))
        libs = load_config(config_path)
        if libs:
            register_libraries(libs)
            _logger.info(f"[Bootstrap] ✅ Registered {len(libs)} template libraries.")
        else:
            _logger.warning("[Bootstrap] No libraries found in config.")
    except Exception as e:
        _logger.warning(f"[Bootstrap] Library loader failed: {e}")

    # 4. HX / CX / JSX runtimes
    _initialize_runtimes()

    _logger.info("🚀 HyperX bootstrap sequence complete.")
    if debug:
        _logger.debug("Debug mode active.")
    return True


# ─────────────────────────────────────────────
# 2️⃣  Runtime Initializers
# ─────────────────────────────────────────────
def _initialize_runtimes():
    """Initialize HX, CX, JSX runtimes if available."""
    runtimes = {
        "HX": "hyperx.loader.hx_loader.init_hx",
        "CX": "hyperx.loader.cx_loader.init_cx",
        "JSX": "hyperx.loader.jsx_loader.init_jsx",
    }

    for name, path in runtimes.items():
        module, func = path.rsplit(".", 1)
        try:
            mod = import_module(module)
            getattr(mod, func)()
            _logger.info(f"[Bootstrap] ✅ {name} runtime initialized.")
        except ModuleNotFoundError:
            _logger.debug(f"[Bootstrap] {name} loader not found — skipped.")
        except Exception as e:
            _logger.warning(f"[Bootstrap] {name} initialization failed: {e}")

def run_bootstrap():
    """CLI entrypoint for the HyperX bootstrap process."""
    from hyperx.bootstrap.bs_loader import initialize
    initialize(debug=True)
    
# ─────────────────────────────────────────────
# 3️⃣  CLI / Standalone execution
# ─────────────────────────────────────────────
if __name__ == "__main__":
    initialize(debug=True)
    _logger.info("✅ HyperX bootstrap standalone execution complete.")
    
    
    