import argparse
import sys, os, re, subprocess
from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("cli_parser")
_logger.info("cli_parser initialized")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hyperx",
        description="HyperX CLI — Declarative Framework & System Tools"
    )
    sub = parser.add_subparsers(dest="command")

    # ───────── Build ─────────
    build = sub.add_parser("build", help="Generate dashboards, views, and URLs for a Django app")
    build.add_argument("app_label", help="App label containing models")
    build.add_argument("--output-dir", default=None, help="Output directory (defaults to app folder)")
    build.add_argument("--templates-dir", default="templates", help="Templates folder (relative to app)")
    build.add_argument("--silent", action="store_true", help="Suppress verbose output")

    # ───────── Install ─────────
    install = sub.add_parser("install", help="Install HyperX into Django settings")
    install.add_argument("settings_path", nargs="?", help="Path to settings.py")
    install.add_argument("--no-backup", action="store_true")

    # ───────── Check ─────────
    check = sub.add_parser("check", help="Validate HyperX installation")
    check.add_argument("--verbose", action="store_true")

    # ───────── Audit ─────────
    audit = sub.add_parser("audit", help="Run system environment audit")
    audit.add_argument("--json", help="Optional path for JSON report")

    # ───────── Post-install ─────────
    sub.add_parser("postinstall", help="Run cleanup and next steps")

    # ───────── Watch ─────────
    watch = sub.add_parser("watch", help="Monitor HyperX dataset watcher")
    watch.add_argument("--refresh", type=int, default=5, help="Refresh interval (seconds)")


    parser.add_argument("--version", action="version", version="HyperX CLI 1.0.0")


    return parser
