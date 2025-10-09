#!/usr/bin/env python3
"""
HyperX Command Line Interface (CLI)
=====================================
Unified system & Django operations for HyperX framework.

Usage:
    hyperx install <path/to/settings.py>   → Add HyperX to Django project
    hyperx system-install                  → Install watcher + environment
    hyperx audit [--json] [path]           → Generate live system audit
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from hyperx.core_install_hyperx import (
    ensure_env,
    summarize,
    install_dataset_watcher,
    find_django_settings,
    HyperXInstaller,
)


import os
import time
import shutil
import subprocess
from datetime import datetime

def tail_journalctl(unit: str, lines: int = 20):
    """Fetch the last N lines of a systemd service log."""
    try:
        return subprocess.getoutput(f"journalctl -u {unit} -n {lines} --no-pager")
    except Exception:
        return "(⚠️ journalctl not available or insufficient permissions)"


def watcher_status():
    """Check watcher service status using systemctl."""
    try:
        status = subprocess.getoutput("systemctl is-active hyperx-dataset-watch.service").strip()
        if status == "active":
            return "🟢 ACTIVE", "✅"
        elif status == "inactive":
            return "⚪ INACTIVE", "⏸️"
        elif status == "failed":
            return "🔴 FAILED", "❌"
        else:
            return f"⚠️ {status.upper()}", "⚠️"
    except Exception:
        return "❓ UNKNOWN", "⚠️"


def watch_dashboard(refresh=5):
    """Live terminal dashboard showing HyperX watcher status."""
    if os.geteuid() != 0:
        print("⚠️ Root privileges recommended to access systemctl logs.")
        print("💡 Try: sudo hyperx watch\n")

    cols = shutil.get_terminal_size().columns
    unit_name = "hyperx-dataset-watch.service"
    print("🔭 HyperX Watcher Dashboard")
    print("──────────────────────────────────────────────────────")

    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            state, icon = watcher_status()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"🕓 {now}")
            print("──────────────────────────────────────────────────────")
            print(f"📡 Service:  {unit_name}")
            print(f"💾 Status:   {state}")
            print(f"🧩 Uptime:   {subprocess.getoutput(f'systemctl show -p ActiveEnterTimestamp {unit_name}').split('=')[-1].strip()}")
            print("──────────────────────────────────────────────────────")
            print(f"📜 Recent Logs (last 15 lines):")
            print("──────────────────────────────────────────────────────")
            logs = tail_journalctl(unit_name, lines=15)
            print("\n".join(logs.splitlines()[-15:]))
            print("──────────────────────────────────────────────────────")
            print(f"🔄 Refreshing every {refresh}s — press Ctrl+C to exit.")
            time.sleep(refresh)

    except KeyboardInterrupt:
        print("\n👋 Exiting HyperX Watcher Dashboard.")


def main():
    parser = argparse.ArgumentParser(prog="hyperx", description="HyperX System and Django CLI")
    sub = parser.add_subparsers(dest="command")

    # Django install
    install = sub.add_parser("install", help="Integrate HyperX into Django settings")
    install.add_argument("settings_path", nargs="?", help="Path to Django settings.py")
    install.add_argument("--no-backup", action="store_true", help="Skip creating backup")
        # Watcher Dashboard
    sub.add_parser("watch", help="Live monitor for HyperX dataset watcher")

    # System install
    sub.add_parser("system-install", help="Install HyperX watcher service and environment")

    # Audit
    audit = sub.add_parser("audit", help="Generate live environment audit")
    audit.add_argument("--json", nargs="?", const="/var/log/hyperx_audit.json",
                       help="Export audit as JSON (default: /var/log/hyperx_audit.json)")

    args = parser.parse_args()

    if args.command == "install":
        settings_path = args.settings_path or find_django_settings()
        if not settings_path:
            print("Could not find Django settings.py.")
            sys.exit(1)

        installer = HyperXInstaller(settings_path)
        success = installer.install(create_backup=not args.no_backup)
        summarize(ensure_env())
        if success:
            print("HyperX installed into Django project successfully.")
        else:
            sys.exit(1)

    elif args.command == "system-install":
        print("Starting HyperX system installation...")
        ensure_env()
        install_dataset_watcher()
        summarize(ensure_env())
        print("System-level setup complete.")

    elif args.command == "audit":
        print("Running HyperX environment audit...")
        key = ensure_env()
        summarize(key, report_path=args.json)
        print("Audit completed successfully.")
    
    elif args.command == "watch":
        watch_dashboard(refresh=args.refresh, auto_restart=args.restart)

        
    else:
        parser.print_help()
