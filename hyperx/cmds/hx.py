#!/usr/bin/env python3
"""Auto-generated Click CLI — DO NOT EDIT."""

from hyperx.kernel.hx_monitor import run_hall_monitor
from hyperx.bootstrap.bs_loader import run_bootstrap
import click
import json
from hyperx.logger.hx_logger import load_logger
_logger = load_logger("hx")
_logger.info("hx cli initialized [dev]")

@click.group()
def cli():
    click.echo(click.style("\n╔══════════════════════════════════════════╗", fg="cyan", bold=True))
    click.echo(click.style(f"║        HYPERX CLI  —  DEV MODE          ║", fg="cyan", bold=True))
    click.echo(click.style("╚══════════════════════════════════════════╝\n", fg="cyan", bold=True))

@cli.command(name="hall_monitor")
def hall_monitor():
    """Run hall_monitor command"""
    run_hall_monitor()


@cli.command(name="bootstrap")
def bootstrap():
    """Run bootstrap command"""
    run_bootstrap()

@cli.command(hidden=True)
def system_info():
    """Show generator build info"""
    info = {
        "build_mode": "dev",
        "build_time": "2025-10-16 09:08:36 UTC",
        "command_count": 2,
        "root_path": "/home/faron/Public/gits/hyperx-htmx_2"
    }
    click.echo(click.style("HyperX CLI Build Info", fg="yellow", bold=True))
    click.echo(json.dumps(info, indent=2))

if __name__ == "__main__":
    cli()

def main():
    cli()
