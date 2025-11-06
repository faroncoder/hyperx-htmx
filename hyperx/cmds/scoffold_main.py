#!/usr/bin/env python3
"""
scoffold_main.py
──────────────────────────────────────────────
Auto-generate HyperX CLI entrypoint by scanning
Python files under hyperx/ for any run_*() functions.

Usage:
    python -m hyperx.cmds.scoffold_main --mode [dev|public]
"""

import os, re, sys, argparse, json
from datetime import datetime, timezone
from pathlib import Path
from hyperx.logger.hx_logger import load_logger

_logger = load_logger("scoffold_main")
_logger.info("🧩 scoffold_main initialized")

# ─────────────────────────────
# 0. Path setup
# ─────────────────────────────
ROOT = Path(__file__).resolve().parents[2]  # project root
sys.path.insert(0, str(ROOT))
PACKAGE_DIR = ROOT / "hyperx"
CMDS_DIR = ROOT / "hyperx" / "cmds"

# ─────────────────────────────
# 1. Helpers
# ─────────────────────────────
def find_run_functions(path: Path):
    """Find all functions that start with run_ in a given file."""
    pattern = re.compile(r"^\s*def\s+(run_[a-zA-Z0-9_]+)\s*\(", re.MULTILINE)
    try:
        return pattern.findall(path.read_text())
    except Exception:
        return []

def scan_tree(root: Path):
    """Recursively scan for Python files with run_ functions."""
    cmds = []
    for dirpath, dirnames, files in os.walk(root):
        # Skip cache, static, etc.
        dirnames[:] = [d for d in dirnames if d not in {"__pycache__", "static"}]
        for f in files:
            if not f.endswith(".py") or f == "__init__.py":
                continue
            file = Path(dirpath) / f
            rel = file.relative_to(ROOT).with_suffix("")
            mod = ".".join(rel.parts)
            for fn in find_run_functions(file):
                cmds.append((fn, mod))
    return cmds

# ─────────────────────────────
# 2. CLI generator
# ─────────────────────────────
def scaffold_main(mode="dev"):
    _logger.info(f"Building HyperX CLI in {mode.upper()} mode")
    all_cmds = scan_tree(PACKAGE_DIR)
    _logger.info(f"Discovered {len(all_cmds)} run_* functions.")

    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    target = CMDS_DIR / "hx.py"

    imports, registrations = [], []
    for fn, mod in all_cmds:
        name = fn.replace("run_", "")
        imports.append(f"from {mod} import {fn}")
        registrations.append(f"""
@cli.command(name="{name}")
def {name}():
    \"\"\"Run {name} command\"\"\"
    {fn}()
""")

    banner = f"""
import click
import json
from hyperx.logger.hx_logger import load_logger
_logger = load_logger("hx")
_logger.info("hx cli initialized [{mode}]")

@click.group()
def cli():
    click.echo(click.style("\\n╔══════════════════════════════════════════╗", fg="cyan", bold=True))
    click.echo(click.style(f"║        HYPERX CLI  —  {mode.upper()} MODE          ║", fg="cyan", bold=True))
    click.echo(click.style("╚══════════════════════════════════════════╝\\n", fg="cyan", bold=True))
"""

    system_info = f"""
@cli.command(hidden=True)
def system_info():
    \"\"\"Show generator build info\"\"\"
    info = {{
        "build_mode": "{mode}",
        "build_time": "{build_time}",
        "command_count": {len(all_cmds)},
        "root_path": "{ROOT}"
    }}
    click.echo(click.style("HyperX CLI Build Info", fg="yellow", bold=True))
    click.echo(json.dumps(info, indent=2))
"""

    footer = """
if __name__ == "__main__":
    cli()

def main():
    cli()
"""

    out = (
        "#!/usr/bin/env python3\n"
        '"""Auto-generated Click CLI — DO NOT EDIT."""\n\n'
        + "\n".join(imports)
        + banner
        + "\n".join(registrations)
        + system_info
        + footer
    )

    target.write_text(out)
    print(f"✅ Generated Click CLI → {target} ({len(all_cmds)} commands)")

# ─────────────────────────────
# 3. Entrypoint
# ─────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["dev", "public"], default="dev")
    args = p.parse_args()
    scaffold_main(args.mode)
