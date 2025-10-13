"""
cx_router.py
────────────────────────────────────────────
Routes CX vectors of the form:
    entity:type:opac:function:command
to registered handlers.
"""
from hypxerx.bin.logger.hx_logger import *
_logger = load_logger("cx_router")
_logger.info("cx_router initialized")
import os, sys, re, json, hmac, hashlib
from pathlib import Path
from hyperx.lib.cx.cx_unix.cx_validator import SignatureValidator
from hyperx.lib.cx.cx_unix.cx_policy import PolicyRegistry
from hyperx.lib.cx.cx_unix.cx_engine import CXEngine
from hyperx.lib.cx.cx_unix.cx_vector import CXVector

from importlib import import_module
from hyperx.lib.cx.cx_links import run_cx_record_vector as cx_record_vector
from hyperx.lib.cx.cx_links import run_cx_summarize as cx_summarize
import json, os, sys, time
_

# optional Recorder bridge
try:
    from hyperx.bin.kernel.hx_recorder import Recorder
except Exception:
    Recorder = None


class cx_Router:
    """Router for CX vectors."""
    _routes = {}

    # ─────────────── registration ───────────────
    @classmethod
    def cx_register(cls, pattern, func):
        """
        Register a handler.
        pattern -> "entity:type:function:command"
        func -> callable(parts, payload)
        """
        cls._routes[pattern] = func
        _logger.debug(f"[cx_router] registered {pattern} → {func.__name__}")

    # ─────────────── dispatch ───────────────
    @classmethod
    def cx_dispatch(cls, cx_vector, payload=None):
        """
        Decode and send a CX vector to the right handler.
        """
        if not cx_vector:
            return
        parts = cx_vector.split(":")
        if len(parts) < 5:
            _logger.warning(f"[cx_router] invalid vector: {cx_vector}")
            return

        entity, vtype, opac, function, command = parts
        payload = payload or {}

        # possible key variants
        keys = [
            f"{entity}:{vtype}:{function}:{command}",
            f"{entity}:{vtype}:{function}:*",
            f"{entity}:*:{function}:{command}",
            f"*:{vtype}:{function}:{command}",
            f"*:*:{function}:{command}",
        ]

        for k in keys:
            if k in cls._routes:
                try:
                    _logger.debug(f"[cx_router] dispatch → {k}")
                    cls._routes[k](parts, payload)
                    # bridge to Recorder
                    if Recorder:
                        Recorder.check_in("cx_router")
                        Recorder.heartbeat("cx_router")
                    # record vector in ledger
                    cx_record_vector(cx_vector, payload)
                    return
                except Exception as e:
                    _logger.error(f"[cx_router] handler {k} failed: {e}")
                    if Recorder:
                        Recorder.red_alert("cx_router", f"handler {k} failed: {e}")
                    return

        _logger.debug(f"[cx_router] no route for {cx_vector}")

    # ─────────────── plugin loader ───────────────
    @classmethod
    def cx_load_plugins(cls):
        """Import any hyperx.plugins.*_routes modules so they self-register."""
        import pkgutil, hyperx.plugins
        for _, modname, _ in pkgutil.iter_modules(hyperx.plugins.__path__):
            if modname.endswith("_routes"):
                try:
                    import_module(f"hyperx.plugins.{modname}")
                    _logger.debug(f"[cx_router] loaded {modname}")
                except Exception as e:
                    _logger.warning(f"[cx_router] load failed for {modname}: {e}")

    # ─────────────── summary ───────────────
    @classmethod
    def cx_list_routes(cls):
        return list(cls._routes.keys())

    @classmethod
    def cx_summary(cls):
        """Print active routes and a snapshot of recent CX events."""
        _logger.info(f"[cx_router] active routes: {len(cls._routes)}")
        for r in cls._routes:
            _logger.info(f"   ↳ {r}")
        try:
            _logger.info("[cx_router] recent CX events:")
            _logger.info(cx_summarize())
        except Exception as e:
            _logger.debug(f"[cx_router] summarize failed: {e}")

# ───────────────
#  CLI interface
# ───────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="CX Router CLI — inspect or dispatch CX vectors."
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Show active routes and recent CX events."
    )
    parser.add_argument(
        "--dispatch", metavar="CXVECTOR",
        help="Dispatch a CX vector manually, e.g. 'hyperx.logger:log:0.3:record:write'"
    )
    parser.add_argument(
        "--payload", metavar="JSON", default="{}",
        help='Optional JSON payload for --dispatch (e.g. \'{"msg":"hi"}\')'
    )

    args = parser.parse_args()

    from hyperx.lib.cx.cx_links import run_cx_init_db as cx_init_db
    cx_init_db()
    cx_Router.cx_load_plugins() 
    

    if args.summary:
        cx_Router.cx_summary()
    elif args.dispatch:
        try:
            data = json.loads(args.payload)
        except Exception:
            data = {}
        cx_Router.cx_dispatch(args.dispatch, data)
    else:
        parser.print_help()
