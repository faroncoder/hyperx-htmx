import subprocess

def tail_journalctl(unit: str, lines: int = 20) -> str:
    """Fetch the last N lines of a systemd service log."""
    try:
        return subprocess.getoutput(f"journalctl -u {unit} -n {lines} --no-pager")
    except Exception:
        return "(⚠️ journalctl not available or insufficient permissions)"

def watcher_status(unit="hyperx-dataset-watch.service") -> str:
    """Return status emoji + state string."""
    try:
        status = subprocess.getoutput(f"systemctl is-active {unit}").strip()
        return {
            "active": "🟢 ACTIVE",
            "inactive": "⚪ INACTIVE",
            "failed": "🔴 FAILED"
        }.get(status, f"⚠️ {status.upper()}")
    except Exception:
        return "❓ UNKNOWN"
