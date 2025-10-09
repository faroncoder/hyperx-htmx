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

import os
import sys
import time
import shutil
import subprocess
from datetime import datetime
import argparse
from pathlib import Path
from hyperx.core.core import *
from hyperx.opt.hyperx.core_install_hyperx import *

# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

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
            return "🟢 ACTIVE"
        if status == "inactive":
            return "⚪ INACTIVE"
        if status == "failed":
            return "🔴 FAILED"
        return f"⚠️ {status.upper()}"
    except Exception:
        return "❓ UNKNOWN"


def watch_dashboard(refresh=5):
    """Live terminal dashboard showing HyperX watcher status."""
    if os.geteuid() != 0:
        print("⚠️  Root privileges recommended to access systemctl logs.\n💡 Try: sudo hyperx watch\n")

    unit_name = "hyperx-dataset-watch.service"

    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            state = watcher_status()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("🔭 HyperX Watcher Dashboard")
            print("──────────────────────────────────────────────")
            print(f"🕓 {now}")
            print(f"📡 Service:  {unit_name}")
            print(f"💾 Status:   {state}")
            print(f"🧩 Uptime:   {subprocess.getoutput(f'systemctl show -p ActiveEnterTimestamp {unit_name}').split('=')[-1].strip()}")
            print("──────────────────────────────────────────────")
            print("📜 Recent Logs (last 15 lines):")
            print("──────────────────────────────────────────────")
            logs = tail_journalctl(unit_name, lines=15)
            print("\n".join(logs.splitlines()[-15:]))
            print("──────────────────────────────────────────────")
            print(f"🔄 Refreshing every {refresh}s — press Ctrl+C to exit.")
            time.sleep(refresh)
    except KeyboardInterrupt:
        print("\n👋 Exiting HyperX Watcher Dashboard.")


# ---------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="hyperx", description="HyperX System and Django CLI")
    sub = parser.add_subparsers(dest="command")

    # Django install
    install = sub.add_parser("install", help="Integrate HyperX into Django settings")
    install.add_argument("settings_path", nargs="?", help="Path to Django settings.py")
    install.add_argument("--no-backup", action="store_true", help="Skip creating backup")

    # Watcher dashboard
    watch = sub.add_parser("watch", help="Live monitor for HyperX dataset watcher")
    watch.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds")

    # System install
    sub.add_parser("system-install", help="Install HyperX watcher service and environment")

    # Audit
    audit = sub.add_parser("audit", help="Generate live environment audit")
    audit.add_argument("--json", nargs="?", const="/var/log/hyperx_audit.json",
                       help="Export audit as JSON (default: /var/log/hyperx_audit.json)")

    args = parser.parse_args()

    # ---------------- install ----------------
    if args.command == "install":
        settings_path = args.settings_path or find_django_settings()
        if not settings_path:
            print("❌ Could not find Django settings.py.")
            sys.exit(1)

        from pathlib import Path
        import shutil
        import subprocess

        repo = "https://github.com/faroncoder/hyperx-elements.git"
        target_dir = Path("../hyperx_elements")

        # Always replace the existing directory
        if target_dir.exists():
            print(f"🧹 Removing existing {target_dir} before cloning new version...")
            try:
                shutil.rmtree(target_dir)
                print("✅ Old hyperx_elements removed successfully.")
            except Exception as e:
                print(f"❌ Failed to remove old {target_dir}: {e}")
                sys.exit(1)

        print(f"📦 Cloning HyperX Elements → {target_dir}")
        subprocess.run(["git", "clone", repo, str(target_dir)], check=True)
        print("✅ hyperx_elements repository cloned successfully.")


        installer = HyperXInstaller(settings_path)
        success = installer.install(create_backup=not args.no_backup)
        if success:
            print("✅ HyperX installed into Django project successfully.")
        else:
            sys.exit(1)

    # ---------------- system-install ----------------
    elif args.command == "system-install":
        print("Starting HyperX system installation...")
        ensure_env()
        install_dataset_watcher()
        summarize(ensure_env())
        print("✅ System-level setup complete.")

    # ---------------- audit ----------------
    elif args.command == "audit":
        print("Running HyperX environment audit...")
        key = ensure_env()
        summarize(key, report_path=args.json)
        print("✅ Audit completed successfully.")

    # ---------------- watch ----------------
    elif args.command == "watch":
        watch_dashboard(refresh=args.refresh)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
