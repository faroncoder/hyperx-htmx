from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("jsx_backparser")
_logger.info("jsx_backparser initialized")

import os, sys, re, json, hmac, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from hyperx.bin.cli.kernel.hx_recorder import Recorder
from bs4 import BeautifulSoup



try:
    from hyperx.bin.cli.kernel.hx_recorder import Recorder
except Exception:
    Recorder = None

recorder = Recorder() if callable(Recorder) else None


def backparse_html(file_path: Path, output_dir="./output"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    html = Path(file_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Example transformation
    for btn in soup.find_all("button"):
        btn.name = "hx:button"
        btn["hx-click"] = "auto:infer"

    out_path = output_dir / Path(file_path).name
    out_path.write_text(str(soup), encoding="utf-8")

    recorder.log_event("backparse_complete", file=str(out_path))
    return out_path


def run_backparse(args=None):
    """
    CLI entrypoint: convert captured HTML into HyperX <hx:*> markup.
    Usage:
        hyperx backparse --file /tmp/hyperx_snapshots/index.html
    """
    from pathlib import Path
    file_path = Path(getattr(args, "file", "./output/index.html"))
    out_dir = getattr(args, "out", "./output")

    parsed = backparse_html(file_path, output_dir=out_dir)
    print(f"✅ Parsed HX template: {parsed}")
