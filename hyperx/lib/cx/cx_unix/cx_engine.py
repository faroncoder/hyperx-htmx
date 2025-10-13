from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("cx_engine")
_logger.info("cx_engine initialized")

import os, sys, re, json, hmac, hashlib
from pathlib import Path



class CXEngine:
    """Declarative execution kernel for CX vectors."""

    def __init__(self, policy_registry, validator):
        self._registry = {}              # (entity,function) → handler
        self.policy = policy_registry
        self.validator = validator

    # ─────────────────────────────────────────────
    # Registration
    # ─────────────────────────────────────────────
    def register(self, entity, function, handler):
        self._registry[(entity, function)] = handler
        logger.info(f"Registered handler {entity}:{function} → {handler.__name__}")

    # ─────────────────────────────────────────────
    # Execution
    # ─────────────────────────────────────────────
    def execute(self, cxlink, context):
        """Execute a single CXLink after validation."""
        if not cxlink:
            return {"error": "empty link"}

        entity = cxlink.get("entity")
        function = cxlink.get("function")
        command = cxlink.get("command")
        extras = cxlink.get("extras", [])

        # 1. validate signature
        if not self.validator.verify(cxlink):
            logger.warning(f"Signature invalid for {entity}:{function}")
            return {"error": "signature invalid"}

        # 2. policy check
        if not self.policy.is_allowed(entity, function, context):
            logger.warning(f"Policy blocked {entity}:{function}")
            return {"error": "policy denied"}

        # 3. run handler
        handler = self._registry.get((entity, function))
        if not handler:
            return {"error": f"no handler for {entity}:{function}"}

        try:
            result = handler(command=command, extras=extras, **context)
            logger.info(f"{entity}:{function}:{command} executed successfully")
            return {"ok": True, "result": result}
        except Exception as e:
            logger.exception(f"Handler error {entity}:{function}: {e}")
            return {"error": str(e)}
