from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("cx_policy")
_logger.info("cx_policy initialized")

import os, sys, re, json, hmac, hashlib
from pathlib import Path


class PolicyRegistry:
    """Simple policy registry loaded from YAML or dict."""

    def __init__(self, policy_source=None):
        self.rules = {}
        if isinstance(policy_source, dict):
            self.rules = policy_source
        elif isinstance(policy_source, str):
            self.load_from_file(policy_source)

    def load_from_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.rules = yaml.safe_load(f) or {}
            _logger.info(f"Policy file loaded: {path}")
        except Exception as e:
            _logger.error(f"Failed to load policy file: {e}")

    def is_allowed(self, entity, function, context):
        """Check if entity:function is allowed for the given user/context."""
        user_role = getattr(context.get("user"), "role", "guest")
        entity_rules = self.rules.get(entity, {})
        allowed = entity_rules.get("allow", [])
        denied = entity_rules.get("deny", [])
        if f"{function}:{user_role}" in denied:
            return False
        if f"{function}:{user_role}" in allowed or "*" in allowed:
            return True
        return False
