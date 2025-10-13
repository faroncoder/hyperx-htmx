# hyperx/core/hall_monitor.py
"""
Hall Monitor — Oversees worker threads, maintains checklist,
writes hall_monitor.json, and reports attendance to Recorder.
"""

from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("hyperx.hallmonitor")
_logger.info("Boot sequence initiated")
import threading, time, json, os
from pathlib import Path
from hyperx.bin.cli.kernel.hx_worker import WorkerThread as worker
from hyperx.bin.cli.kernel.hx_recorder import Recorder

from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("hyperx.hallmonitor.worker")
_logger.info("Hall Monitor Worker initialized")


REPORTS_DIR = Path(__file__).resolve().parent / "_reports"
REPORTS_DIR.mkdir(exist_ok=True)
CHECKLIST_PATH = REPORTS_DIR / "hall_monitor.json"
MAX_JSON_SIZE = 50_000  # bytes ≈ 50 KB

_lock = threading.Lock()


class HallMonitor(threading.Thread):
    """Monitors worker threads and updates checklist + Recorder attendance."""

    def __init__(self, check_interval=5, timeout=60):
        super().__init__(daemon=True, name="HallMonitor")
        self.check_interval = check_interval
        self.timeout = timeout
        self.checklist = self._load_checklist()
        Recorder.check_in("hall_monitor")

    # ───────────────────────────────
    #  Internal helpers
    # ───────────────────────────────
    def _load_checklist(self):
        if CHECKLIST_PATH.exists():
            try:
                with open(CHECKLIST_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_checklist(self):
        with _lock:
            with open(CHECKLIST_PATH, "w") as f:
                json.dump(self.checklist, f, indent=2)

    def _red_alert_if_large(self):
        if CHECKLIST_PATH.exists() and CHECKLIST_PATH.stat().st_size > MAX_JSON_SIZE:
            reason = "hall_monitor.json too large — possible rogue worker(s)"
            logger.error(f"[HallMonitor] 🚨 {reason}")
            Recorder.red_alert("hall_monitor", reason)

    # ───────────────────────────────
    #  Main loop
    # ───────────────────────────────
    def run(self):
        logger.info("[HallMonitor] 🧭 started")
        while True:
            Recorder.heartbeat("hall_monitor")     # attendance ping
            self.scan_workers()
            self._save_checklist()
            self._red_alert_if_large()
            time.sleep(self.check_interval)

    # ───────────────────────────────
    #  Worker scanning
    # ───────────────────────────────
    def scan_workers(self):
        active_workers = list(worker.heartbeat.keys())
        now = time.time()

        # remove finished workers
        for name in list(self.checklist.keys()):
            if name not in active_workers:
                self.checklist.pop(name, None)
                logger.debug(f"[HallMonitor] ✅ {name} cleared from checklist")

        # update or add active workers
        for name in active_workers:
            last_seen = worker.heartbeat.get(name, now)
            delta = now - last_seen
            status = "ok" if delta < self.timeout else "timeout"
            task = worker.registry.get(name, {}).get("current_task", "unknown")

            self.checklist[name] = {
                "last_seen": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(last_seen)),
                "status": status,
                "delta": round(delta, 2),
                "task": task,
            }

            if status == "timeout":
                logger.warning(f"[HallMonitor] {name} unresponsive for {delta:.1f}s")
                Recorder.red_alert("hall_monitor", f"{name} timed out ({task})")
                worker.restart_thread(name)
        logger.debug(f"[HallMonitor] checklist updated: {len(self.checklist)} entries")


def run_hall_monitor():
    hm = HallMonitor()
    hm.start()
    return hm
