# hyperx/core/recorder.py
"""
hx_status.py
────────────────────────────────────────────
Quick dashboard for HyperX runtime health.

────────────────────────────────────────────
Python method decorators refresher
────────────────────────────────────────────
Regular method
    def foo(self, ...):
        • First arg → self (the instance)
        • Use when working with that object’s data.

Class method
    @classmethod
    def foo(cls, ...):
        • First arg → cls (the class itself)
        • Works on data shared by all instances.

Static method
    @staticmethod
    def foo(...):
        • No automatic first arg.
        • Pure helper or utility function; logically
          belongs in the class but independent of it.

Summary:
    self → “this object”
    cls  → “the class”
    none → “just a helper”

Recorder – centralized tally + attendance system.
Keeps running JSON summaries of metrics and module heartbeats.
────────────────────────────────────────────
"""

from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("hyperx.recorder")
_logger.info("Recorder initialized")

from threading import Lock
import time, json, os

_lock = Lock()

class Recorder:
    _data = {
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "workers_active": 0,
        "workers_restarted": 0,
        "tasks_completed": 0,
        "plugins_loaded": 0,
        "alerts": [],
    }
    _attendance = {}

    # ─────────────── Tally handling ───────────────
    @classmethod
    def _save(cls):
        with _lock, open(RECORD_PATH, "w") as f:
            json.dump(cls._data, f, indent=2)

    @classmethod
    def _save_attendance(cls):
        with _lock, open(ATTEND_PATH, "w") as f:
            json.dump(cls._attendance, f, indent=2)

    @classmethod
    def add_task(cls, worker_name, task):
        """
        Record a completed task and update both recorder.json and hx_status.sqlite3.
        """
        try:
            cls._data["tasks_completed"] = cls._data.get("tasks_completed", 0) + 1
            # mirror to the status DB
            hx_record_stat("recorder", "tasks_completed", cls._data["tasks_completed"])
            # persist to JSON
            cls._save()
        except Exception as e:
            cls._data.setdefault("alerts", []).append(
                {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "source": "recorder.add_task", "reason": str(e)}
            )
            cls._save()
        

    @classmethod
    def worker_event(cls, name, action):
        if action == "start":
            cls._data["workers_active"]  = cls._data.get("workers_active", 0) + 1
            hx_record_stat("recorder", "workers_active", cls._data["workers_active"])
            cls._save()
        elif action == "stop":
            cls._data["workers_active"] = max(0, cls._data["workers_active"] - 1)
            hx_record_stat("recorder", "workers_active", cls._data["workers_active"])
            cls._save()
        elif action == "restart":
            cls._data["workers_restarted"] = cls._data.get("workers_restarted", 0) + 1
            hx_record_stat("recorder", "workers_restarted", cls._data["workers_restarted"]) 
            cls._save()

    @classmethod
    def plugin_loaded(cls, name):
        cls._data["plugins_loaded"] = cls._data.get("plugins_loaded", 0) + 1
        logger.debug(f"[Recorder] plugin registered: {name}")
        cls._save()

    @classmethod
    def red_alert(cls, source, reason):
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
            "reason": reason,
        }
        cls._data["alerts"].append(entry)
        logger.error(f"[Recorder] 🚨 alert from {source}: {reason}")
        cls._save()

    # ─────────────── Attendance handling ───────────────
    @classmethod
    def check_in(cls, module):
        cls._attendance[module] = {
            "last_seen": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "online"
        }
        logger.debug(f"[Recorder] {module} checked in")
        cls._save_attendance()

    @classmethod
    def check_out(cls, module):
        if module in cls._attendance:
            cls._attendance[module]["status"] = "offline"
            cls._attendance[module]["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.debug(f"[Recorder] {module} checked out")
            cls._save_attendance()

    @classmethod
    def heartbeat(cls, module):
        """Periodic ping from modules to confirm they are alive."""
        if module not in cls._attendance:
            cls.check_in(module)
        else:
            cls._attendance[module]["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
            cls._attendance[module]["status"] = "online"
            cls._save_attendance()
