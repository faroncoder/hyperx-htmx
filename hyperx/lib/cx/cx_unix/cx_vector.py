from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("cx_engine")
_logger.info("cx_engine initialized")
import os, sys, re, json, hmac, hashlib
from pathlib import Path

_logger = load_logger("cx_vector")
_logger.info("cx_vector initialized")


class CXVector:
    """A group of CXLinks with an optional control link."""

    def __init__(self, entity, secure=False):
        self.entity = entity
        self.secure = secure
        self.links = []
        self.control_link = None

    def add(self, cxlink, control=False):
        if control:
            self.control_link = cxlink
        else:
            self.links.append(cxlink)

    def execute_all(self, engine, context):
        """Execute all CXLinks; require control link if secure."""
        if self.secure and not self._authorized(engine, context):
            logger.warning(f"Control link authorization failed for {self.entity}")
            return {"error": "authorization failed"}

        results = []
        for link in self.links:
            results.append(engine.execute(link, context))
        return results

    def _authorized(self, engine, context):
        """Validate control link via engine policy/validator."""
        if not self.control_link:
            return False
        return (
            engine.validator.verify(self.control_link)
            and engine.policy.is_allowed(
                self.control_link.get("entity"),
                self.control_link.get("function"),
                context,
            )
        )
