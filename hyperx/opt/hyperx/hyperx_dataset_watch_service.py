#!/usr/bin/env python3
"""
──────────────────────────────────────────────
HyperX Dataset Watcher - Service Installer
──────────────────────────────────────────────
Automatically provisions the HyperX Dataset Watcher
and ensures Django is running before launching.

Features:
  ✅ Auto-check Django readiness
  ✅ Installs/updates systemd service
  ✅ Uses .env / decouple config (OPENAI_API_KEY)
──────────────────────────────────────────────
"""

import os, sys, subprocess, time, logging
from pathlib import Path
from dotenv import load_dotenv
from decouple import config

# ─────────────────────────────────────────────
# Load environment
# ─────────────────────────────────────────────
BASE_DIR = Path("/opt/hyperx")
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

OPENAI_KEY = config("OPENAI_API_KEY", default="")
DJANGO_SETTINGS_MODULE = config("DJANGO_SETTINGS_MODULE", default="config.settings")

# ─────────────────────────────────────────────
# Core paths
# ─────────────────────────────────────────────
WATCH_SCRIPT = BASE_DIR / "hyperx_dataset_watch_transfer.sh"
AUTOGEN_SCRIPT = BASE_DIR / "ai_schema_autogen.py"
SERVICE_NAME = "hyperx-dataset-watch.service"
SERVICE_PATH = Path(f"/etc/systemd/system/{SERVICE_NAME}")
LOG_FILE = Path("/var/log/hyperx_service_installer.log")

# ─────────────────────────────────────────────
# Logger setup
# ─────────────────────────────────────────────
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("hyperx_installer")

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def run(cmd, check=True, timeout=15):
    """Run shell command safely and capture output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if check and result.returncode != 0:
            log.error(f"❌ Command failed: {cmd}\n{result.stderr}")
            raise RuntimeError(result.stderr)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log.warning(f"⏳ Command timed out: {cmd}")
        return ""

def ensure_permissions():
    """Ensure scripts are executable."""
    for script in (WATCH_SCRIPT, AUTOGEN_SCRIPT):
        if script.exists():
            script.chmod(0o755)
            log.info(f"✅ Executable permission ensured: {script}")
        else:
            log.error(f"❌ Missing file: {script}")
            sys.exit(1)

# ─────────────────────────────────────────────
# Django readiness check
# ─────────────────────────────────────────────
def wait_for_django():
    """
    Wait for Django (Gunicorn / manage.py runserver)
    to be fully booted before launching watcher.
    """
    log.info("🧠 Checking for Django server readiness...")

    for _ in range(30):  # ~30s grace period
        # Detect by process name (gunicorn / runserver)
        proc_check = run("pgrep -f 'manage.py runserver|gunicorn' || true", check=False)
        if proc_check:
            log.info("✅ Django process detected, proceeding with watcher.")
            return True
        log.info("⏳ Django not ready yet, waiting 1s...")
        time.sleep(1)

    log.warning("⚠️ Django did not start within 30s. Watcher will still start.")
    return False

# ─────────────────────────────────────────────
# Write systemd unit
# ─────────────────────────────────────────────
def write_systemd_unit():
    content = f"""[Unit]
Description=HyperX Dataset Watcher & AI Schema Generator
After=network.target
Requires=network.target

[Service]
Type=simple
ExecStartPre=/bin/bash -c 'python3 {__file__} --wait-django'
ExecStart=/bin/sh {WATCH_SCRIPT}
Restart=always
User=www-data
WorkingDirectory={BASE_DIR}
Environment="DJANGO_SETTINGS_MODULE={DJANGO_SETTINGS_MODULE}"
Environment="OPENAI_API_KEY={OPENAI_KEY}"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
"""
    SERVICE_PATH.write_text(content)
    log.info(f"✅ Systemd unit written: {SERVICE_PATH}")

# ─────────────────────────────────────────────
# Enable + start service
# ─────────────────────────────────────────────
def enable_and_start():
    run("systemctl daemon-reexec || true", check=False)
    run("systemctl daemon-reload")
    run(f"systemctl enable {SERVICE_NAME}")
    run(f"systemctl restart {SERVICE_NAME}")
    status = run(f"systemctl is-active {SERVICE_NAME}", check=False)
    if status == "active":
        log.info(f"🚀 {SERVICE_NAME} is running.")
    else:
        log.warning(f"⚠️ {SERVICE_NAME} failed to start properly.")

# ─────────────────────────────────────────────
# Entrypoints
# ─────────────────────────────────────────────
def install_service():
    log.info("──────────────────────────────────────")
    log.info("🧩 Installing HyperX Dataset Watcher")
    log.info("──────────────────────────────────────")

    ensure_permissions()
    write_systemd_unit()
    enable_and_start()

    log.info("✅ Install complete — logs at /var/log/hyperx_service_installer.log")

def wait_django_entry():
    wait_for_django()
    sys.exit(0)

# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ Must run as root (sudo).")
        sys.exit(1)

    if "--wait-django" in sys.argv:
        wait_django_entry()
    else:
        install_service()
