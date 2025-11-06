"""
hx_logger.py
────────────────────────────────────────────
Neutral logging kernel for all frameworks.
Now also feeds events to Recorder for live telemetry.
"""

import logging
import logging.config
import json
import os
import re
import inspect
from pathlib import Path
from datetime import datetime, timedelta
from decouple import config
from colorama import Fore, Style, init as colorama_init
from pythonjsonlogger import jsonlogger
import traceback
from responses import logger


# ─────────────────────────────────────────────
#  Color Setup
# ─────────────────────────────────────────────
colorama_init(autoreset=True)
COLOR_LEVELS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA,
}


class ColorFormatter(logging.Formatter):
    """Adds ANSI colors to level names without altering the rest of the format."""
    def format(self, record):
        level_color = COLOR_LEVELS.get(record.levelname, "")
        record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


# ─────────────────────────────────────────────
#  Core Config
# ─────────────────────────────────────────────
BASE_LOG = Path(os.environ.get("LOG_DIR", str(Path(__file__).resolve().parent.parent / "logs")))
LOG_ROOT = Path(__file__).resolve().parent.parent / "logs"
LOG_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR = Path(config("LOG_DIR", default=str(LOG_ROOT)))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "system.log"

BASE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) :: %(message)s"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","file":"%(filename)s","line":%(lineno)d,"msg":%(message)s}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
        "standard": {"format": BASE_FORMAT},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_FILE),
            "maxBytes": 5_000_000,
            "backupCount": 5,
            "formatter": "standard",
            "level": "DEBUG",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}

logging.config.dictConfig(LOGGING_CONFIG)
root_logger = logging.getLogger()

# Colorize console handler
for handler in root_logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setFormatter(ColorFormatter(BASE_FORMAT))

#─────────────────────────────────────────────
#  Module Logger Factory
# ─────────────────────────────────────────────
def get_module_log_path(root: Path | str = None, filename: str = None) -> logging.Logger:
    """Return a per-module logger with colorized console and its own file output."""
    env_log_dir = os.getenv("LOG_DIR")
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_name = module.__name__ if module else "unknown"

    base_root = Path(root or env_log_dir or LOG_ROOT)
    base_root.mkdir(parents=True, exist_ok=True)

    parts = module_name.split(".")
    subdir = base_root.joinpath(*parts[:-1])
    subdir.mkdir(parents=True, exist_ok=True)
    fname = filename or f"{parts[-1]}.log"
    fpath = subdir / fname

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Inherit console handlers from root
    for h in root_logger.handlers:
        if isinstance(h, logging.StreamHandler):
            h.setFormatter(ColorFormatter(BASE_FORMAT))
        logger.addHandler(h)

    # Add per-module file handler
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(fpath)
               for h in logger.handlers):
        file_handler = logging.FileHandler(fpath, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(BASE_FORMAT))
        logger.addHandler(file_handler)

    return logger




# ─────────────────────────────────────────────
#  Recorder Bridge (optional)
# ─────────────────────────────────────────────
try:
    from kernel.hx_recorder import Recorder
except Exception:
    Recorder = None


# ─────────────────────────────────────────────
#  Log Cluster (for aggregation)
# ─────────────────────────────────────────────
class LogCluster:
    """Collect log lines across all files within a time window (default ±300s)."""
    TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})")

    def __init__(self, pivot: datetime = None, window_sec: int = 300):
        base_dir = Path(os.getenv("LOG_DIR", LOG_DIR))
        self.base_dir = base_dir
        self.pivot = pivot
        self.window_sec = window_sec
        self.entries = self.gather_recent_logs()

    def gather_recent_logs(self):
        entries = []
        for log_file in self.base_dir.glob("*.log"):
            try:
                with log_file.open("r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        m = self.TS_RE.search(line)
                        if not m:
                            continue
                        ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
                        entries.append((log_file.name, ts, line.strip()))
            except Exception as e:
                print(f"⚠️ Could not read {log_file}: {e}")

        if not entries:
            return []

        entries.sort(key=lambda x: x[1])
        pivot = self.pivot or entries[-1][1]
        window = timedelta(seconds=self.window_sec)

        cluster = [
            (file, ts, line)
            for file, ts, line in entries
            if abs(ts - pivot) <= window
        ]
        return sorted(cluster, key=lambda x: x[1])

    def __str__(self):
        lines = [f"Log Cluster around {self.pivot} (±{self.window_sec}s):"]
        for file, ts, line in self.entries:
            lines.append(f"[{file}] {ts} :: {line}")
        return "\n".join(lines)


# ─────────────────────────────────────────────
#  Event Logger
# ─────────────────────────────────────────────
def log_event(event, namespace=None, level="info", **fields):
    """
    Universal structured logger_
    Example:
        log_event("compile_complete", system="hyperx", worker="W-1")
    """
    namespace = namespace or Path(__file__).stem
    level = (level or "info").lower()

    payload = {"event": event, "script_name": namespace, "ts": datetime.utcnow().isoformat(), **fields}
    msg = json.dumps(payload, default=str, ensure_ascii=False)

    # Recorder hook
    if Recorder and hasattr(Recorder, "log_event"):
        try:
            Recorder.log_event(event, namespace=namespace, **fields)
        except Exception as e:
            msg += f" (Recorder log_event failed: {e})"

    root = logging.getLogger()
    getattr(root, level, root.info)(msg)




    # # ─────────────────────────────────────────────
    # #  Helper Factory (replaces loadselflogger)
    # # ─────────────────────────────────────────────
    # def log_functions(namespace: str | None = None, boolean: bool = None) -> dict:
    #     """
    #     Returns a dictionary with a logger and bound log functions
    #     for the given namespace (usually the module name).

    #     Example:
    #         logs = log_functions("hyperx.core.worker")
    #         logs["log_info"]("worker_started")
    #     """
    #     ns = namespace or Path(__file__).stem

    #     def _log_event(event, level="info", **fields):
    #         log_event(event, namespace=ns, level=level, **fields)

    #     return {
    #         "_log_event": _log_event,
    #         "_log_info":  lambda e, **f: _log_event(e, "info", **f),
    #         "_log_warn":  lambda e, **f: _log_event(e, "warning", **f),
    #         "_log_error": lambda e, **f: _log_event(e, "error", **f),
    #         "_log_debug": lambda e, **f: _log_event(e, "debug", **f),
    #         "_log_exception": lambda e, **f: _log_event(e, "error", exception=traceback.format_exc(), **f),
    #         "_logger":  lambda e, **f: _log_event(e, "info", **f),
    #     }


# ## ALIAS for backward compatibility
# # Define a basic logger object with log_event-based methods for compatibility.
# class loggerAlias:
#     @staticmethod
#     def info(msg, **kwargs):
#         log_event(msg, level="info", **kwargs)
#     @staticmethod
#     def debug(msg, **kwargs):
#         log_event(msg, level="debug", **kwargs)
#     @staticmethod
#     def warning(msg, **kwargs):
#         log_event(msg, level="warning", **kwargs)
#     @staticmethod
#     def error(msg, **kwargs):
#         log_event(msg, level="error", **kwargs)
#     @staticmethod
#     def exception(msg, **kwargs):
#         log_event(msg, level="error", exception=traceback.format_exc(), **kwargs)
#     @staticmethod
#     def critical(msg, **kwargs):
#         log_event(msg, level="critical", **kwargs)

# logger = loggerAlias


class TimingHandler(logging.Handler):
    """
    Tracks start/end of a logging session and reports ✅ success or 🔴 failure.
    """
    def __init__(self, label="start"):
        super().__init__()
        self.label = label
        self.start_time = datetime.now()
        self.failed = False
        print(f"{Fore.CYAN}🟢 [{self.label}] Started at {self.start_time}{Style.RESET_ALL}")

    def emit(self, record):
        # if the record level is ERROR or higher, flag failure
        if record.levelno >= logging.ERROR:
            self.failed = True

    def close(self):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        if self.failed:
            print(f"{Fore.RED}🔴 [{self.label}] FAILED at {self.end_time} (Duration: {duration:.2f}s){Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ [{self.label}] Completed at {self.end_time} (Duration: {duration:.2f}s){Style.RESET_ALL}")
        super().close()


    # ─────────────────────────────────────────────
    #  Wrapper Functions
    # ─────────────────────────────────────────────

    def logger_start(_logger, label=None):
        """
        Start timing for the given logger_
        Returns the TimingHandler so it can be stopped later with `_logger_stop()`.
        """
        handler = TimingHandler(label or getattr(_logger, "name", "session"))
        _logger.addHandler(handler)
        return handler
        """
        Stops timing for a logger session and prints ✅ or 🔴 depending on outcome.
        """
        if handler:
            try:
                handler.close()
            except Exception as e:
                print(f"{Fore.RED}⚠️ Could not close timing handler: {e}{Style.RESET_ALL}")
        logging.shutdown()



def load_logger(namespace: str | None = None, boolean: bool = None):
    """
    Initialize and return a logger for the given namespace.
    Example:
        _logger = load_logger("hyperx.bin.cli.logger.setenv")
    """
    namespace = str(namespace or Path(__file__).stem)

    logger = logging.getLogger(namespace)
    logger.setLevel(logging.DEBUG)

    # Ensure color formatter is applied for console handlers
    for h in root_logger.handlers:
        if isinstance(h, logging.StreamHandler):
            h.setFormatter(ColorFormatter(BASE_FORMAT))
            logger.addHandler(h)

    # Add a per-module file handler
    module_log = LOG_DIR / f"{namespace.replace('.', '_')}.log"
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(module_log)
               for h in logger.handlers):
        fh = logging.FileHandler(module_log, encoding="utf-8")
        fh.setFormatter(logging.Formatter(BASE_FORMAT))
        logger.addHandler(fh)

    logger.propagate = False
    return logger



class loggerAlias:
    @staticmethod
    def logger(msg, **kwargs):
        log_event(msg, level="info", **kwargs)
        return logger(msg, **kwargs)
        
    @staticmethod
    def info(msg, **kwargs):
        log_event(msg, level="info", **kwargs)
        logger_info = logger = loggerAlias
        return logger_info(msg, **kwargs) or logger(msg, **kwargs)

    @staticmethod
    def debug(msg, **kwargs):
        log_event(msg, level="debug", **kwargs)
        logger_debug = loggerAlias.debug(msg, **kwargs)
        return logger_debug

    @staticmethod
    def warning(msg, **kwargs):
        log_event(msg, level="warning", **kwargs)
        logger_warning = loggerAlias.warning(msg, **kwargs)
        return logger_warning

    @staticmethod
    def error(msg, **kwargs):
        log_event(msg, level="error", **kwargs)
        logger_error = loggerAlias.error(msg, **kwargs)
        return logger_error
    @staticmethod
    def exception(msg, **kwargs):
        log_event(msg, level="error", exception=traceback.format_exc(), **kwargs)
        logger_exception = loggerAlias.exception(msg, **kwargs)
        return logger_exception
    @staticmethod
    def critical(msg, **kwargs):
        log_event(msg, level="critical", **kwargs)            
        logger_critical = loggerAlias.critical(msg, **kwargs)
        return logger_critical(logger.critical, **kwargs)
    @staticmethod
    def start(namespace=Path(__file__).stem, label="session"):
        logger_obj = logging.getLogger(str(namespace))
        handler = TimingHandler(label=label)
        logger_obj.addHandler(handler)
        return handler

    @staticmethod
    def stop(handler=None):
        if handler:
            try:
                handler.close()
            except Exception as e:
                print(f"{Fore.RED}⚠️ Could not close timing handler: {e}{Style.RESET_ALL}")
        logging.shutdown()

        




# ─────────────────────────────────────────────
#  Enhanced run_logger
# ─────────────────────────────────────────────
def _run_logger(namespace, timed=False):
    """
    Initializes a logger and (optionally) attaches a TimingHandler.
    Automatically prints 🟢 start and ✅/🔴 end.
    """
    # logger_time = load_logger(namespace, timed=timed)

   
    
    load_logger({namespace})
    
 
    
    log_event(logging.info("log_event ready"))

    # return both the logger and its timing handler for control
    
    
    





