from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("jsx_pipeline")
_logger.info("jsx_pipeline initialized")

from pathlib import Path
from playwright.sync_api import sync_playwright
from hyperx.bin.cli.kernel.hx_recorder import Recorder
from bs4 import BeautifulSoup
import json
from celery import shared_task
from hyperx.bin.cli.jsx_parser.crawler import *
from hyperx.bin.cli.jsx_parser.backparser import *
from hyperx.bin.cli.jsx_parser.jsc_extractor import *



try:
    from hyperx.bin.cli.kernel.hx_recorder import Recorder
except Exception:
    Recorder = None

recorder = Recorder() if callable(Recorder) else None



@shared_task
def capture_and_parse(url: str):
    """Full pipeline: crawl → parse → extract JS+CSS assets."""
    recorder.log_event("task_start", url=url)
    snapshot = crawl_route(url)
    parsed = backparse_html(snapshot)
    extract_assets(parsed)        # renamed call here
    recorder.log_event("task_complete", url=url)
    return str(parsed)

def run_pipeline(args=None):
    """
    CLI entrypoint: launch the full Celery React→HyperX pipeline.
    Usage:
        hyperx pipeline --url http://localhost:3000
    """
    from hyperx.lib.jsx_parser.tasks import capture_and_parse
    url = getattr(args, "url", "http://localhost:3000")
    capture_and_parse.delay(url)
    print(f"🚀 Pipeline task queued for {url}")
