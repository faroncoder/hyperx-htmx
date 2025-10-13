#!/usr/bin/env python3
"""
scoffold_main.py
──────────────────────────────────────────────
Auto-generate HyperX CLI main entrypoint by scanning
all Python files under bin/ and lib/.

Usage:
    python bin/cli/utils/scoffold_main.py --mode [dev|public]
"""
import os, re, sys, argparse
from datetime import datetime
from pathlib import Path
from hyperx.bin.cli.logger.hx_logger import *

_logger = load_logger("scoffold_main")
_logger.info("scoffold_main initialized")

ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PARENT_DIR = ROOT / "hyperx"
BIN_DIR = PARENT_DIR / "bin"
LIB_DIR = PARENT_DIR / "lib"
CLI_DIR = BIN_DIR / "cli"
TARGET_OUTFILE = CLI_DIR / "hx.py"
root = ROOT


def find_run_functions(path: Path):
    pat = re.compile(r"^\s*def\s+(run_[a-zA-Z0-9_]+)\s*\(", re.MULTILINE)
    try:
        return pat.findall(path.read_text())
    except Exception:
        return []


def scan_tree(root: Path):
    cmds = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".py") or f in ("__init__.py", "scoffold_main.py"):
                continue
            file = Path(dirpath) / f
            rel = file.relative_to(ROOT).with_suffix("")
            mod = ".".join(rel.parts)
            for fn in find_run_functions(file):
                cmds.append((fn, mod))
    return cmds


def scaffold_main(mode="dev"):
    _logger.info(f"Building Click CLI in {mode.upper()} mode")

    all_cmds = []
    for d in [BIN_DIR, LIB_DIR]:
        if d.exists():
            all_cmds += scan_tree(d)

    from datetime import datetime, UTC   # already imported, just add UTC if missing
    build_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z")


    banner = f"""
import click, json, sys
from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("hx-cli")
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

    imports, registrations = [], []
    for fn, mod in all_cmds:
        try:
            doc = Path(ROOT / Path(mod.replace(".", "/") + ".py")).read_text()
            if mode == "public" and ("[ADMIN]" in doc or "admin_only=True" in doc):
                continue
        except Exception:
            pass
        name = fn.replace("run_", "")
        imports.append(f"from {mod} import {fn}")
        registrations.append(f"""
@cli.command(name="{name}")
def {name}():
    \"\"\"Run {name} command\"\"\"
    {fn}()
""")

    footer = """
if __name__ == "__main__":
    cli()
    
def main():
    cli()
"""

    out = (
        "#!/usr/bin/env python3\n"
        '"""Auto-generated Click CLI — DO NOT EDIT."""\n'
        + "\n".join(imports)
        + banner
        + "\n".join(registrations)
        + system_info
        + footer
    )

    TARGET_OUTFILE.write_text(out)
    print(f"✅ Generated Click CLI → {TARGET_OUTFILE}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["dev", "public"], default="dev")
    args = p.parse_args()
    scaffold_main(args.mode)
