"""
crawler.py
────────────────────────────────────────────
Captures live DOM snapshots from a running React dev server.
"""
from hyperx.bin.cli.kernel.hx_recorder import Recorder
from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("jsx_crawler")
_logger.info("jsx_crawler initialized")
import os, sys, re, json, hmac, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright





try:
    from hyperx.bin.cli.kernel.hx_recorder import Recorder
except Exception:
    Recorder = None

recorder = Recorder() if callable(Recorder) else None



def crawl_route(url: str, output_dir="./output"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    recorder.log_event("crawler_start", url=url)

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

    recorder.log_event("crawler_finish", file=str(fpath))
    return fpath


def run_crawl(args=None):
    """
    CLI entrypoint: crawl live React app and save HTML snapshots.
    Usage:
        hyperx crawl --url http://localhost:3000
    """
    url = getattr(args, "url", None) or "http://localhost:3000"
    output = getattr(args, "out", "/tmp/hyperx_snapshots")

    from hyperx.core.hx_recorder import Recorder
    recorder = Recorder()
    recorder.log_event("cli_crawl_start", url=url)

    fpath = crawl_route(url, output)
    recorder.log_event("cli_crawl_finish", file=str(fpath))
    print(f"✅ Snapshot saved at: {fpath}")
