#!/usr/bin/env python3
"""Auto-generated Click CLI — DO NOT EDIT."""
from hyperx.bin.cli.jsx_parser.jsc_extractor import run_jsc
from hyperx.bin.cli.jsx_parser.backparser import run_backparse
from hyperx.bin.cli.jsx_parser.crawler import run_crawl
from hyperx.bin.cli.jsx_parser.tasks import run_pipeline
from hyperx.bin.cli.installer.hyperx_install import run_postinstall
from hyperx.bin.cli.installer.hyperx_install import run_install
from hyperx.bin.cli.kernel.hx_monitor import run_hall_monitor
from hyperx.bin.cli.celery.beat import run_beat
from hyperx.bin.cli.celery.core_celery import run_worker
from hyperx.bin.cli.celery.core_celery import run_crawl
from hyperx.bin.cli.celery.core_celery import run_pipeline
from hyperx.bin.cli.celery.tasks import run_capture_and_parse
from hyperx.bin.cli.generator.core import run_build
from hyperx.bin.cli.generator.core import run_find_settings
from hyperx.bin.cli.utils.hyperx_diagnostics import run_audit
from hyperx.lib.cx.cx_links import run_cx_init_db
from hyperx.lib.cx.cx_links import run_cx_record_vector
from hyperx.lib.cx.cx_links import run_cx_summarize
from hyperx.lib.cx.cx_links import run_cx_kernel_selftest
import click, json, sys
from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("hx-cli")
_logger.info("hx cli initialized [dev]")

@click.group()
def cli():
    click.echo(click.style("\n╔══════════════════════════════════════════╗", fg="cyan", bold=True))
    click.echo(click.style(f"║        HYPERX CLI  —  DEV MODE          ║", fg="cyan", bold=True))
    click.echo(click.style("╚══════════════════════════════════════════╝\n", fg="cyan", bold=True))

@cli.command(name="jsc")
def jsc():
    """Run jsc command"""
    run_jsc()


@cli.command(name="backparse")
def backparse():
    """Run backparse command"""
    run_backparse()


@cli.command(name="crawl")
def crawl():
    """Run crawl command"""
    run_crawl()


@cli.command(name="pipeline")
def pipeline():
    """Run pipeline command"""
    run_pipeline()


@cli.command(name="postinstall")
def postinstall():
    """Run postinstall command"""
    run_postinstall()


@cli.command(name="install")
def install():
    """Run install command"""
    run_install()


@cli.command(name="hall_monitor")
def hall_monitor():
    """Run hall_monitor command"""
    run_hall_monitor()


@cli.command(name="beat")
def beat():
    """Run beat command"""
    run_beat()


@cli.command(name="worker")
def worker():
    """Run worker command"""
    run_worker()


@cli.command(name="crawl")
def crawl():
    """Run crawl command"""
    run_crawl()


@cli.command(name="pipeline")
def pipeline():
    """Run pipeline command"""
    run_pipeline()


@cli.command(name="capture_and_parse")
def capture_and_parse():
    """Run capture_and_parse command"""
    run_capture_and_parse()


@cli.command(name="build")
def build():
    """Run build command"""
    run_build()


@cli.command(name="find_settings")
def find_settings():
    """Run find_settings command"""
    run_find_settings()


@cli.command(name="audit")
def audit():
    """Run audit command"""
    run_audit()


@cli.command(name="cx_init_db")
def cx_init_db():
    """Run cx_init_db command"""
    run_cx_init_db()


@cli.command(name="cx_record_vector")
def cx_record_vector():
    """Run cx_record_vector command"""
    run_cx_record_vector()


@cli.command(name="cx_summarize")
def cx_summarize():
    """Run cx_summarize command"""
    run_cx_summarize()


@cli.command(name="cx_kernel_selftest")
def cx_kernel_selftest():
    """Run cx_kernel_selftest command"""
    run_cx_kernel_selftest()

@cli.command(hidden=True)
def system_info():
    """Show generator build info"""
    info = {
        "build_mode": "dev",
        "build_time": "2025-10-13 01:29:11 UTC",
        "command_count": 19,
        "root_path": "/home/faron/Public/gits/hyperx-htmx"
    }
    click.echo(click.style("HyperX CLI Build Info", fg="yellow", bold=True))
    click.echo(json.dumps(info, indent=2))

if __name__ == "__main__":
    cli()
    
def main():
    cli()
