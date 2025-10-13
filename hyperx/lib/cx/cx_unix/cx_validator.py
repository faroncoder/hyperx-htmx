from hyperx.bin.cli.logger.hx_logger import *


_logger = load_logger("cx_engine")
_logger.info("cx_engine initialized")
import os, sys, re, json, hmac, hashlib
from pathlib import Path

class SignatureValidator:
    """Placeholder signature validator."""

    def __init__(self, secret=None):
        self.secret = secret or os.environ.get("CXUNIX_SECRET", "default-key")

    def sign(self, data_str):
        return hmac.new(self.secret.encode(), data_str.encode(), hashlib.sha256).hexdigest()

    def verify(self, cxlink):
        raw = cxlink.get("raw", "")
        sig = cxlink.get("signature")
        if not sig:
            logger.debug("No signature present")
            return False
        expected = self.sign(raw)
        return hmac.compare_digest(expected, sig)
