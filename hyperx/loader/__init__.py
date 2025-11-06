import os, sys, importlib
from pathlib import Path
from hyperx.logger.hx_logger import load_logger
_logger = load_logger("hyperx loaders")
_logger.info("hyperx loader initalized")



def initialize():

    # ─────────────────────────────
    # 1. Logger setup
    # ─────────────────────────────
    from hyperx.logger.bootstrap_logger import bootstrap_logger
    bootstrap_logger()

    # ─────────────────────────────
    # 2. Element Loader (your new script)
    # ─────────────────────────────
    try:
        from hyperx.loader.element_loader import load_elements
        count = load_elements()
        _logger.info(f"✅ Element loader initialized ({count} elements discovered).")
    except Exception as e:
        _logger.warning(f"[Loader] Element loader failed: {e}")

    # ─────────────────────────────
    # 3. Initialize HX, CX, JSX
    # ─────────────────────────────
    from hyperx.loader.hx_loader import init_hx
    # from cx.cx_loader import init_cx
    # from .jsx_loader import init_jsx
    init_hx()
    # init_cx()
    # init_jsx()

    _logger.info("✅ HyperX loader sequence complete.")
