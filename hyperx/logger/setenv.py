# setenv.py
import os
from pathlib import Path
from hyperx.logger.hx_logger import *

_logger = load_logger("hyperx.cmds.workers.setenv")
_logger.info("setenv initialized")


def main():
    handler = TimingHandler("setenv")
    _logger.addHandler(handler)

    try:
        # Fallback path if LOG_DIR not set
        BASE_LOG = Path(os.environ.get("LOG_DIR", str(Path(__file__).resolve().parent.parent / "logs")))
        BASE_LOG.mkdir(parents=True, exist_ok=True)

        REPORTS_DIR = BASE_LOG / "_reports"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        RECORD_PATH = REPORTS_DIR / "record.log"
        MONITOR_PATH = REPORTS_DIR / "monitor.log"
        WORKER_PATH = REPORTS_DIR / "worker.log"
        REGISTRAR_PATH = REPORTS_DIR / "registrar.log"
        ATTEND_PATH = REPORTS_DIR / "attendance.log"

        for path in [RECORD_PATH, MONITOR_PATH, WORKER_PATH, REGISTRAR_PATH, ATTEND_PATH]:
            if not path.exists():
                _logger.warning(f"Creating missing file: {path}")
                path.touch()
            else:
                _logger.debug(f"File exists: {path}")

        _logger.info("Environment verification complete.")

    except Exception as e:
        _logger.exception(f"Setup failed: {e}")
    finally:
        handler.close()


# ─────────────────────────────────────────────
# One-time executor (safe bootstrap)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Default to current repo logs folder if LOG_DIR not exported
    BASE_LOG = Path(os.environ.get("LOG_DIR", str(Path(__file__).resolve().parent.parent / "logs")))
    BASE_LOG.mkdir(parents=True, exist_ok=True)

    SENTINEL = BASE_LOG / ".initialized"

    if SENTINEL.exists():
        print("🟢 Environment already initialized. Skipping.")
    else:
        try:
            print("🟢 Initializing environment for the first time...")
            main()                # perform the directory and file setup
            SENTINEL.touch()      # mark as initialized
            print(f"✅ Initialization complete. Sentinel created at {SENTINEL}")
        except Exception as e:
            print(f"🔴 Initialization failed: {e}")
            raise
