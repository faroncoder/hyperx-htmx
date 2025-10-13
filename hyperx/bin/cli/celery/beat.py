import os
import subprocess
from pathlib import Path
from celery import Celery, shared_task
from playwright.sync_api import sync_playwright

from hyperx.bin.cli.logger.hx_logger import * 
from hyperx.bin.cli.kernel.hx_recorder import *
from hyperx.bin.cli.jsx_parser.jsc_extractor import *
from hyperx.bin.cli.jsx_parser.backparser import *

def run_beat(args=None):
    port = getattr(args, "port", 5556)
    subprocess.run(["celery", "-A", "hx", "beat", "-l", "info"], check=True)


