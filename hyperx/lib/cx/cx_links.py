"""
cx_links.py
────────────────────────────────────────────
CX ledger: persistent SQLite sink for all CX traffic.
"""

import sqlite3, time, logging, json
from pathlib import Path
from hyperx.lib.cx.cx_unix.cx_validator import *
from hyperx.lib.cx.cx_unix.cx_policy import *
from hyperx.lib.cx.cx_unix.cx_engine import *
from hyperx.lib.cx.cx_unix.cx_vector import *


from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("cx_links")
_logger.info("cx_links initialized")


from pathlib import Path
import os

REPORTS_DIR = os.environ.get("REPORTS_DIR")
if not REPORTS_DIR:
    # default to a local _reports directory
    REPORTS_DIR = Path(__file__).resolve().parent / "_reports"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
else:
    REPORTS_DIR = Path(REPORTS_DIR)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = REPORTS_DIR / "cx_log.sqlite3"


# ─────────────── setup ───────────────
def run_cx_init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cx_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            entity TEXT,
            type TEXT,
            opac REAL,
            function TEXT,
            command TEXT,
            payload TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity ON cx_log(entity)")
    con.commit()
    con.close()
    _logger.info(f"[cx_links] initialized → {DB_PATH}")

# ─────────────── record ───────────────
def run_cx_record_vector(cx_vector:str, payload:dict=None):
    payload = payload or {}
    parts = cx_vector.split(":")
    if len(parts) < 5:
        _logger.warning(f"[cx_links] invalid vector: {cx_vector}")
        return
    entity, vtype, opac, function, command = parts
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            INSERT INTO cx_log (ts, entity, type, opac, function, command, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ts, entity, vtype, float(opac),
              function, command, json.dumps(payload, ensure_ascii=False)))
        con.commit()
        con.close()
        logger.debug(f"[cx_links] logged {cx_vector}")
    except Exception as e:
        _logger.error(f"[cx_links] failed to record {cx_vector}: {e}")

# ─────────────── summarize ───────────────
def run_cx_summarize(limit=20):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        SELECT ts, entity, type, function, command
        FROM cx_log
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    con.close()
    return "\n".join(f"{ts} | {entity}:{type_}:{function}:{command}" for ts, entity, type_, function, command in rows)

run_cx_init_db()



def run_cx_kernel_selftest(args=None):
    """[ADMIN] Full CX kernel self-test."""
    ...
