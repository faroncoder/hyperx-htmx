import os, time, subprocess
from datetime import datetime
from hyperx.bin.cli.utils.systemd import tail_journalctl, watcher_status

def watch_dashboard(refresh: int = 5, unit_name="hyperx-dataset-watch.service"):
    """Live terminal dashboard showing HyperX watcher status."""
    if os.geteuid() != 0:
        print("⚠️  Root privileges recommended.\n💡 Try: sudo hyperx watch\n")

    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            state = watcher_status(unit_name)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("🔭 HyperX Watcher Dashboard")
            print("───────────────────────────────")
            print(f"🕓 {now}\n📡 Service: {unit_name}\n💾 Status:  {state}")
            uptime = subprocess.getoutput(
                f"systemctl show -p ActiveEnterTimestamp {unit_name}"
            ).split("=")[-1].strip()
            print(f"🧩 Uptime:  {uptime}")
            print("───────────────────────────────")
            print("📜 Recent Logs (last 15 lines):")
            print("───────────────────────────────")
            logs = tail_journalctl(unit_name, lines=15)
            print("\n".join(logs.splitlines()[-15:]))
            print("───────────────────────────────")
            print(f"🔄 Refreshing every {refresh}s — Ctrl+C to exit.")
            time.sleep(refresh)
    except KeyboardInterrupt:
        print("\n👋 Exiting HyperX Watcher Dashboard.")
