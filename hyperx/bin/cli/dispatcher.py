from hyperx.bin.cli.commands.install import run_install
from hyperx.bin.cli.commands.check import run_check
from hyperx.bin.cli.commands.audit import run_audit
from hyperx.bin.cli.commands.postinstall import run_postinstall
from hyperx.bin.cli.generator import run_build
from hyperx.bin.cli.monitor import watch_dashboard


def dispatch(args):
    """Route CLI subcommands to their respective functions."""
    cmd = args.command
    if cmd == "build":
        run_build(args.app_label, args.output_dir, args.templates_dir, args.silent)
    elif cmd == "install":
        run_install(args.settings_path, args.no_backup)
    elif cmd == "check":
        run_check(verbose=args.verbose)
    elif cmd == "audit":
        run_audit(json_path=args.json)
    elif cmd == "postinstall":
        run_postinstall()
    elif cmd == "watch":
        watch_dashboard(refresh=args.refresh)
    else:
        print("⚠️ Unknown or missing command. Use: hyperx --help")
