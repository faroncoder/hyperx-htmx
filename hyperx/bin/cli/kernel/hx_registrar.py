from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("hyperx.registrar")
_logger.info("Registrar initialized")

# Get log directory from environment or use default
BASE_LOG = Path(os.environ.get("LOG_DIR", "_reports"))
BASE_LOG.mkdir(exist_ok=True)

REPORTS_DIR = BASE_LOG / "_reports"
REPORTS_DIR.mkdir(exist_ok=True)
RECORD_PATH = REPORTS_DIR / "recorder.json"
ATTEND_PATH = REPORTS_DIR / "attendance.json"
REGISTRAR_PATH = REPORTS_DIR / "registrar.json"
WORKER_PATH = REPORTS_DIR / "workers.json"
MONITOR_PATH = REPORTS_DIR / "hall_monitor.json"


from threading import Lock
import time, json, os




...
class HyperXRegistrar:
    _tag_converters = {}
    _htmx_builders = {}
    _plugins = {}

    @classmethod
    def _write_manifest(cls):
        data = {
            "tags": list(cls._tag_converters.keys()),
            "builders": list(cls._htmx_builders.keys()),
            "plugins": list(cls._plugins.keys()),
            "stats": cls.stats(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(REPORT_PATH, "w") as f:
            json.dump(data, f, indent=2)
        _logger.info(f"[Registrar] manifest written to {REPORT_PATH}")

    @classmethod
    def bootstrap(cls):
        _logger.info("[Registrar] Bootstrapping HyperXRegistrar...")
        from django.apps import apps
        autodiscover('hyperx_plugins')
        _logger.start_timer()
        cls._write_manifest()
        _logger.stop_timer("[Registrar] Bootstrapping completed")