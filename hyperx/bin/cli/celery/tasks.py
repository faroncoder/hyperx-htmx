from celery import shared_task
from hyperx.bin.cli.jsx_parser.crawler import *
from hyperx.bin.cli.jsx_parser.backparser import *
from hyperx.bin.cli.jsx_parser.jsc_extractor import *
from hyperx.bin.cli.logger.hx_logger import *
from pathlib import Path
import json
_logger = load_logger("celery-reactjs_tasks")
_logger.info("celery-reactjs_tasks initialized")




@shared_task
def capture_and_parse(url):
    log_event("capture_and_parse", {url}, locals(), {})
    snapshot = crawl_route(url)
    log_event("crawl_route_complete", {url, snapshot}, locals(), {})    
    parsed = backparse_html(snapshot)
    log_event("backparse_html_complete", {url, snapshot, parsed}, locals(), {})
    extract_assets(parsed)
    log_event("extract_assets_complete", {url, snapshot, parsed}, locals(), {})
    return str(parsed)


def run_capture_and_parse(args=None):
    """
    CLI entrypoint: capture and parse a React route.
    Usage:
        hyperx capture_and_parse --url http://localhost:3000
    """
    url = getattr(args, "url", "http://localhost:3000")
    log_event("run_capture_and_parse", {url}, locals(), {})
    result = capture_and_parse(url)
    log_event("capture_and_parse_complete", {url, result}, locals(), {})
    print(f"✅ Captured and parsed React route: {result}")
    return result

