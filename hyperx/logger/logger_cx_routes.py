"""
Logger CX Routes
────────────────────────────────────────────
Defines CXRouter handlers for logger and alert vectors.
"""

from hyperx.logger.hx_logger import *

_logger = load_logger('hx-logger-cx-routes')
_logger.info("Logger CX Routes module loaded.")    


from cx.cx_router import CXRouter
from kernel.hx_recorder import Recorder


# ─────────────── Handlers ───────────────

def handle_log(parts, payload):
    """Generic log record handler."""
    entity, vtype, opac, function, command = parts
    _logger.info(f"[CXRoute] LOG from {entity}:{function}:{command} | {payload}")   

def handle_alert(parts, payload):
    """Handles alert-type vectors."""
    entity, vtype, opac, function, command = parts
    reason = payload.get("reason", "unspecified")
    _logger.warning(f"[CXRoute] ALERT {entity} → {function}:{command} | reason={reason}")
    Recorder.red_alert(entity, f"{function}:{command} | {reason}")
    _logger.warning(f"[CXRoute] ALERT {entity} → {function}:{command} | reason={reason}")

def handle_restart(parts, payload):
    """Simulates restart action on timeout/critical events."""
    entity, vtype, opac, function, command = parts
    _logger.error(f"[CXRoute] RESTART signal from {entity} | {payload}")
    Recorder.red_alert(entity, "restart triggered (simulated)")
    _logger.error(f"[CXRoute] RESTART signal from {entity} | {payload}")

# ─────────────── Registration ───────────────
CXRouter.register("hyperx.bin.cli.hx_logger:record:write", handle_log)
_logger.info("[Logger CX Routes] write function registered.")

CXRouter.register("*:alert:monitor:timeout", handle_alert)
_logger.info("[Logger CX Routes] alert route registered.")

CXRouter.register("*:alert:monitor:restart", handle_restart)
_logger.info("[Logger CX Routes] restart function registered.")
