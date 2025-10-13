#!/usr/bin/env python3
"""
hx_status.py
────────────────────────────────────────────
Quick dashboard for HyperX runtime health.
"""

import json, logging, os
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent / "_reports"
LOG_DIR     = Path(__file__).resolve().parent / "_logs"
LOG_FILE    = LOG_DIR / "system.log"

def read_json(path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {}

def tail_log(path, lines=10):
    if not path.exists():
        return ["(no log file found)"]
    with open(path, "r", encoding="utf-8") as f:
        data = f.readlines()
        return data[-lines:]

def main():
    print("═══════════════════════════════════════════════════")
    print("   🧠  HyperX / CX Runtime Status")
    print("═══════════════════════════════════════════════════\n")

    # Recorder summary
    rec = read_json(REPORTS_DIR / "recorder.json")
    if rec:
        print("📊 Recorder")
        for k, v in rec.items():
            if isinstance(v, (int, str)):
                print(f"   {k:20}: {v}")
        print()

    # Attendance
    att = read_json(REPORTS_DIR / "attendance.json")
    if att:
        print("👥 Attendance")
        for mod, info in att.items():
            print(f"   {mod:20}: {info.get('status','?')} ({info.get('last_seen','?')})")
        print()

    # Hall Monitor
    hall = read_json(REPORTS_DIR / "hall_monitor.json")
    if hall:
        print("🔎 Hall Monitor")
        for worker, info in hall.items():
            print(f"   {worker:20}: {info.get('status','?')} Δ={info.get('delta','?')}")
        print()

    # Tail log
    print("🧾 Last 10 log entries")
    print("───────────────────────")
    for line in tail_log(LOG_FILE):
        print(" ", line.strip())

    print("\n═══════════════════════════════════════════════════")
    print(" End of HX Status Report")
    print("═══════════════════════════════════════════════════")

if __name__ == "__main__":
    main()

