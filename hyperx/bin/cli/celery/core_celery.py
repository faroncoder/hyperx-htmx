import os
import subprocess
from pathlib import Path
from celery import Celery, shared_task
from playwright.sync_api import sync_playwright

from hyperx.bin.cli.logger.hx_logger import * 
from hyperx.bin.cli.kernel.hx_recorder import *
from hyperx.bin.cli.jsx_parser.jsc_extractor import *
from hyperx.bin.cli.jsx_parser.backparser import *


_logger = load_logger('celery')
_logger.info("Starting Celery worker")


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("hx")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["hyperx.bin.cli", "hyperx.bin.cli.celery"])


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


def run_worker(args=None):
    """CLI: start Celery worker"""
    subprocess.run(["celery", "-A", "hx", "worker", "-l", "info"], check=True)




@shared_task
def crawl_route(url, output_dir="/tmp/hyperx_snapshots"):
    """Celery task: capture a single React route and stream it to HyperX."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(1500)
        html = page.content()
        browser.close()

    fname = url.replace("http://localhost:3000", "").strip("/").replace("/", "_") or "index"
    fpath = Path(output_dir) / f"{fname}.html"
    fpath.write_text(html, encoding="utf-8")

    # immediately stream to HyperX parser
    backparse_html(fpath)
    return str(fpath)


def run_crawl(args=None):
    """
    CLI entrypoint: crawl a React route and save the HTML snapshot.
    Usage:
        hyperx crawl --url http://localhost:3000
    """
    url = getattr(args, "url", "http://localhost:3000")
    out_dir = getattr(args, "out", "/tmp/hyperx_snapshots")
    recorder.log_event("cli_crawl_start", url=url)
    snapshot = crawl_route(url, output_dir=out_dir)
    print(f"✅ Captured React snapshot: {snapshot}")
    recorder.log_event("cli_crawl_complete", url=url)



@shared_task
def capture_and_parse(url: str):
    """Full pipeline: crawl → parse → extract JS+CSS assets."""
    recorder.log_event("capture_and_parse_start", url=url)
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
