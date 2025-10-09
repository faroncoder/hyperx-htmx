#!/usr/bin/env python3
import platform
import shutil
import subprocess
import django
from datetime import datetime
import os
import sys
import argparse
from pathlib import Path
import json
import logging
import time
from django.conf import settings
from typing import Tuple, Optional, List
from ...core.core import *

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class HyperXInstaller:
    """Automatically configures Django settings.py for HyperX integration."""
    
    REQUIRED_APPS = [
        '"django_htmx"',
        '"hyperx"',
    ] 
    
    REQUIRED_MIDDLEWARE = [
        '"django_htmx.middleware.HtmxMiddleware"',
        '"hyperx.middleware.HyperXMiddleware"',
        '"hyperx.middleware.HyperXSecurityMiddleware"',  # Optional
    ]
    
    HYPERX_CONFIG = '''
# ==========================================
# HyperX Configuration
# ==========================================

# HyperX Middleware Configuration  
HYPERX_MIDDLEWARE = {
    'AUTO_VALIDATE_HTMX': True,           # Automatically validate HTMX requests
    'AUTO_PARSE_XTAB': True,              # Automatically parse X-Tab headers  
    'SECURITY_LOGGING': True,             # Enable security event logging
    'PERFORMANCE_TRACKING': True,         # Track request performance
    'STRICT_XTAB_VALIDATION': False,      # Strict X-Tab validation (optional)
}

# HyperX Security Configuration (optional)
HYPERX_SECURITY = {
    'RATE_LIMITING': True,                # Enable rate limiting
    'PATTERN_DETECTION': True,            # Detect suspicious patterns
    'AUTO_BLOCKING': False,               # Auto-block suspicious requests  
    'MAX_REQUESTS_PER_MINUTE': 60,        # Rate limit threshold
}
'''

    def __init__(self, settings_path: str):
        self.settings_path = Path(settings_path)
        self.backup_path = self.settings_path.with_suffix('.py.backup')
        
    def backup_settings(self) -> bool:
        """Create a backup of the original settings file."""
        try:
            content = self.settings_path.read_text()
            self.backup_path.write_text(content)
            print(f"✅ Backup created: {self.backup_path}")
            
        
            if shutil.which("flake8"):
                subprocess.run(
                    ["flake8", ".", "--count", "--select=E9,F63,F7,F82",
                    "--show-source", "--statistics"],
                    check=False,
                )
            else:
                print("⚠️  flake8 not found, skipping syntax check")
                return True
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
            
    def read_settings(self) -> str:
        """Read the current settings file."""
        try:
            return self.settings_path.read_text()
        except Exception as e:
            print(f"❌ Failed to read settings file: {e}")
            return ""
            
    def write_settings(self, content: str) -> bool:
        """Write the modified settings file."""
        try:
            self.settings_path.write_text(content)
            print(f"✅ Settings updated: {self.settings_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to write settings: {e}")
            return False
            
    def find_installed_apps(self, content: str) -> Tuple[int, int]:
        """Find the INSTALLED_APPS section and return start/end line numbers."""
        lines = content.split('\n')
        start_line = -1
        end_line = -1
        bracket_count = 0
        
        for i, line in enumerate(lines):
            if 'INSTALLED_APPS' in line and '=' in line:
                start_line = i
                if '[' in line:
                    bracket_count = line.count('[') - line.count(']')
                continue
                    
            if start_line >= 0:
                bracket_count += line.count('[') - line.count(']')
                if bracket_count == 0 and ']' in line:
                    end_line = i
                    break
                    
        return start_line, end_line
        
    def find_middleware(self, content: str) -> Tuple[int, int]:
        """Find the MIDDLEWARE section and return start/end line numbers."""
        lines = content.split('\n')
        start_line = -1
        end_line = -1
        bracket_count = 0
        
        for i, line in enumerate(lines):
            if 'MIDDLEWARE' in line and '=' in line:
                start_line = i
                if '[' in line:
                    bracket_count = line.count('[') - line.count(']')
                continue
                    
            if start_line >= 0:
                bracket_count += line.count('[') - line.count(']')
                if bracket_count == 0 and ']' in line:
                    end_line = i
                    break
                    
        return start_line, end_line
        
    def add_to_installed_apps(self, content: str) -> Tuple[str, List[str]]:
        """Add HyperX apps to INSTALLED_APPS if not already present."""
        lines = content.split('\n')
        start_line, end_line = self.find_installed_apps(content)
        
        if start_line == -1:
            print("⚠️ INSTALLED_APPS not found in settings file")
            return content, []
            
        # Check if apps are already installed
        apps_section = '\n'.join(lines[start_line:end_line+1])
        missing_apps = []
        
        for app in self.REQUIRED_APPS:
            if app not in apps_section and app.strip('"') not in apps_section:
                missing_apps.append(app)
                
        if not missing_apps:
            print("✅ HyperX apps already in INSTALLED_APPS")
            return content, []
            
        # Add missing apps before the closing bracket
        indent = "    "  # Default indentation
        
        # Try to detect existing indentation
        for i in range(start_line + 1, end_line):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                break
                
        # Insert apps before the closing bracket
        insert_pos = end_line
        for app in missing_apps:
            lines.insert(insert_pos, f"{indent}{app},  # Added by HyperX installer")
            insert_pos += 1
            
        print(f"✅ Added {len(missing_apps)} apps to INSTALLED_APPS")
        return '\n'.join(lines), missing_apps


    


        
    def add_to_middleware(self, content: str) -> Tuple[str, List[str]]:
        """Add HyperX middleware to MIDDLEWARE in the correct position."""
        lines = content.split('\n')
        start_line, end_line = self.find_middleware(content)
        
        if start_line == -1:
            print("⚠️ MIDDLEWARE not found in settings file")
            return content, []
            
        # Check if middleware are already installed
        middleware_section = '\n'.join(lines[start_line:end_line+1])
        missing_middleware = []
        
        for mw in self.REQUIRED_MIDDLEWARE:
            if mw not in middleware_section and mw.strip('"') not in middleware_section:
                missing_middleware.append(mw)
                
        if not missing_middleware:
            print("✅ HyperX middleware already in MIDDLEWARE")
            return content, []
            
        # Find the best insertion point (after CSRF, before Auth)
        insert_pos = end_line  # Default to end
        indent = "    "
        
        for i in range(start_line + 1, end_line):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                # Detect indentation
                indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                
                # Insert after CSRF middleware
                if 'csrf' in line.lower() or 'CsrfViewMiddleware' in line:
                    insert_pos = i + 1
                    break
                # Or before Auth middleware  
                elif 'auth' in line.lower() and 'AuthenticationMiddleware' in line:
                    insert_pos = i
                    break
                    
        # Insert middleware
        for j, mw in enumerate(missing_middleware):
            comment = "# Added by HyperX installer"
            if j == 0:
                comment += " - Core functionality"
            elif j == 1: 
                comment += " - Main middleware"
            else:
                comment += " - Security features (optional)"
                
            lines.insert(insert_pos + j, f"{indent}{mw},  {comment}")
            
        print(f"✅ Added {len(missing_middleware)} middleware to MIDDLEWARE")
        return '\n'.join(lines), missing_middleware


        
    def add_hyperx_config(self, content: str) -> Tuple[str, bool]:
        """Add HyperX configuration at the end of the file."""
        if 'HYPERX_MIDDLEWARE' in content:
            print("✅ HyperX configuration already present")
            return content, False
            
        # Add configuration at the end
        if not content.endswith('\n'):
            content += '\n'
            
        content += self.HYPERX_CONFIG
        print("✅ Added HyperX configuration")
        return content, True
        
        
        if shutil.which("flake8"):
            subprocess.run(
                ["flake8", ".", "--count", "--select=E9,F63,F7,F82",
                "--show-source", "--statistics"],
                check=False,
            )
        else:
            print("⚠️  flake8 not found, skipping syntax check")

        # Check if disclosure already exists
        if 'HyperX Auto-Installer Disclosure' in content:
            return content
            
        # Create disclosure based on what was actually changed
        disclosure_lines = [
            "",
            "# " + "="*70,
            "# HyperX Auto-Installer Disclosure",
            "# " + "="*70,
            f"# This file was automatically modified by HyperX installer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "#",
            "# The following changes were made:",
        ]
        
       

        if changes_made.get('apps_added'):
            disclosure_lines.extend([
                "#",
                "# ✅ INSTALLED_APPS - Added:",
            ])

            for app in (changes_made.get('apps_added') or []):
                clean_app = app.strip('"')
                disclosure_lines.append(f"#    • {clean_app}")
                
                # To run flake8 as a shell command from Python, use subprocess:
        

    def add_hyperx_disclosure(self, content: str, changes_made: dict) -> str:
        """Add disclosure comment explaining what HyperX installer modified."""
        import shutil, subprocess

        # Check if disclosure already exists
        if "HyperX Auto-Installer Disclosure" in content:
            return content

        disclosure_lines = [
            "",
            "# " + "=" * 70,
            "# HyperX Auto-Installer Disclosure",
            "# " + "=" * 70,
            f"# This file was automatically modified by HyperX installer on "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "#",
            "# The following changes were made:",
        ]

        # Optional flake8 check
        if shutil.which("flake8"):
            subprocess.run(
                [
                    "flake8",
                    ".",
                    "--count",
                    "--select=E9,F63,F7,F82",
                    "--show-source",
                    "--statistics",
                ],
                check=False,
            )

        if changes_made.get("apps_added"):
            disclosure_lines.append("#\n# ✅ INSTALLED_APPS - Added:")
            for app in changes_made["apps_added"]:
                clean_app = app.strip('"')
                disclosure_lines.append(f"#    • {clean_app}")

        if changes_made.get("middleware_added"):
            disclosure_lines.append("#\n# ✅ MIDDLEWARE - Added:")
            for mw in changes_made["middleware_added"]:
                mw_name = mw.strip('"').split(".")[-1]
                disclosure_lines.append(f"#    • {mw_name}")




        if changes_made.get("config_added"):
            disclosure_lines.extend(
                [
                    "#",
                    "# ✅ CONFIGURATION - Added:",
                    "#    • HYPERX_MIDDLEWARE settings",
                    "#    • HYPERX_SECURITY settings",
                ]
            )

        disclosure_lines.extend(
            [
                "#",
                "# 🧹 CLEANUP:",
                "#    • Management commands will be auto-removed after installation",
                "#",
                "# 📚 Documentation: https://github.com/faroncoder/hyperx-htmx",
                f"# 💾 Original backup saved as: {self.backup_path.name}",
                "# " + "=" * 70,
            ]
        )

        if not content.endswith("\n"):
            content += "\n"
        content += "\n".join(disclosure_lines) + "\n"
        return content


    def install(self, create_backup: bool = True) -> bool:
            """Main installation method."""
            if not self.settings_path.exists():
                print(f"❌ Settings file not found: {self.settings_path}")
                return False
                
            print(f"🚀 Installing HyperX into {self.settings_path}")
            
            # Create backup
            if create_backup and not self.backup_settings():
                return False
                
            # Read current settings
            content = self.read_settings()
            if not content:
                return False
                
            # Apply modifications and track changes
            changes_made = {}
            
            content, apps_added = self.add_to_installed_apps(content)
            changes_made['apps_added'] = apps_added
            
            content, middleware_added = self.add_to_middleware(content)
            changes_made['middleware_added'] = middleware_added
            
            content, config_added = self.add_hyperx_config(content)
            changes_made['config_added'] = config_added
            
            # Add disclosure if any changes were made
            if any([apps_added, middleware_added, config_added]):
                content = self.add_hyperx_disclosure(content, changes_made)
            
            # Write modified settings
            if not self.write_settings(content):
                return False
                
            print("🎉 HyperX installation completed successfully!")
            print("\n📋 Next steps:")
            print("1. Run: python manage.py migrate")
            print("2. In your templates: {% load hyperx %}")
            print("3. Check the documentation for usage examples")
            
            return True



def find_django_settings() -> Optional[str]:
    """Try to automatically find Django settings file using os.walk search."""
    
    # Walk through current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        # Skip common non-project directories
        dirs[:] = [d for d in dirs if d not in {
            '__pycache__', '.git', '.venv', 'venv', 'env', 
            'node_modules', '.pytest_cache', '.mypy_cache',
            'build', 'dist', '.tox'
        }]
        
        if 'settings.py' in files:
            settings_path = Path(root) / 'settings.py'
            
            # Validate it's a Django project by checking for asgi.py or wsgi.py
            asgi_path = Path(root) / 'asgi.py'
            wsgi_path = Path(root) / 'wsgi.py'
            
            if asgi_path.exists() or wsgi_path.exists():
                print(f"🔍 Found Django project at: {settings_path}")
                return str(settings_path.resolve())
            else:
                # Check if it looks like a Django settings file by content
                try:
                    content = settings_path.read_text()
                    if any(django_marker in content for django_marker in [
                        'DJANGO_SETTINGS_MODULE', 'INSTALLED_APPS', 'MIDDLEWARE',
                        'django.contrib', 'ROOT_URLCONF'
                    ]):
                        print(f"🔍 Found Django settings file at: {settings_path}")
                        return str(settings_path.resolve())
                except:
                    continue
                    
    return None


    def install_hyperx(settings_path: Optional[str] = None) -> bool:
        """Main installation function."""
        if not settings_path:
            settings_path = find_django_settings()
            
        if not settings_path:
            print("❌ Could not find Django settings.py file")
            print("💡 Please specify the path: install_hyperx('/path/to/settings.py')")
            return False
            
        installer = HyperXInstaller(settings_path)
        return installer.install()


        """
    ──────────────────────────────────────────────
    Core Installer for HyperX Environment
    ──────────────────────────────────────────────
    Handles:
    - Initial environment setup
    - Auto .env creation
    - HyperX middleware + service provisioning
    - Dataset watcher activation
    ──────────────────────────────────────────────
    """
    # Additional imports for system-level installation

    try:
        from dotenv import load_dotenv
        from decouple import config
    except ImportError:
        print("⚠️ Optional dependencies not installed: python-dotenv python-decouple")
        load_dotenv = lambda x: None
        config = lambda x, default=None: default





    BASE_DIR = Path("/hyperx/opt/hyperx")
    LOG_FILE = Path("/var/log/hyperx_core_install.log")
    SERVICE_NAME = "hyperx-dataset-watch.service"
    SERVICE_PATH = Path(f"/etc/systemd/system/{SERVICE_NAME}")
    WATCHER_SCRIPT = BASE_DIR / "hyperx_dataset_watch_service.py"
    HYPERX_ENV = BASE_DIR / ".env.example"
    HYPERX_ENV_EXAMPLE = Path("./.env.example")

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    log = logging.getLogger("hyperx_core_install")


    def run(cmd, check=True, timeout=15):
        """Execute a shell command safely."""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            if check and result.returncode != 0:
                log.error(f"❌ Command failed: {cmd}\n{result.stderr}")
                raise RuntimeError(result.stderr)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            log.warning(f"⏳ Command timed out: {cmd}")
            return ""

    # ─────────────────────────────────────────────
    # 1️⃣  Environment Setup
    # ─────────────────────────────────────────────
    def ensure_env(filename: Path = HYPERX_ENV) -> str:
        """Ensure that .env exists or copy from .env.example."""
        if not filename.exists():
            if HYPERX_ENV_EXAMPLE.exists():
                shutil.copy(HYPERX_ENV_EXAMPLE, filename)
                log.info("✅ Copied .env.example → .env")
            else:
                filename.write_text("OPENAI_API_KEY=your-openai-api-key-here\n")
                log.warning("⚠️ Created fallback .env file.")
        load_dotenv(filename)
        return config("OPENAI_API_KEY", default="")

        # ─────────────────────────────────────────────
    # 2️⃣  Django Setup Validation
    # ─────────────────────────────────────────────
    def verify_django_setup():
        """Check Django + middleware integration."""
        try:
            
            django.setup()
            middlewares = getattr(settings, "MIDDLEWARE", [])
            has_hyperx = any("hyperx.middleware.HyperXMiddleware" in m for m in middlewares)
            if has_hyperx:
                log.info("✅ HyperXMiddleware detected in Django settings.")
            else:
                log.warning("⚠️ HyperXMiddleware not found in Django settings.")
            return True
        except Exception as e:
            log.error(f"❌ Django setup check failed: {e}")
            return False


        target_dir = Path("../hyperx_elements")

        if target_dir.exists():
            print(f"⚠️  {target_dir} already exists — skipping git clone.")
        else:
            subprocess.run(
                ["git", "clone", "https://github.com/faroncoder/hyperx-elements.git", str(target_dir)],
                check=True,
            )


    # ─────────────────────────────────────────────
    # 3️⃣  Dataset Watcher Installation
    # ─────────────────────────────────────────────
    def install_dataset_watcher():
        """Run the dataset watcher installer."""
        if not WATCHER_SCRIPT.exists():
            log.warning("⚠️ Dataset watcher script missing; skipping setup.")
            return False
        try:
            log.info("🚀 Installing Dataset Watcher service...")
            run(f"sudo python3 {WATCHER_SCRIPT}")
            log.info("✅ Dataset Watcher installed successfully.")
            return True
        except Exception as e:
            log.error(f"❌ Watcher installation failed: {e}")
            return False

        # ─────────────────────────────────────────────
        # 4️⃣  Watcher Health & Auto-Restart
        # ─────────────────────────────────────────────
        def check_watcher_health(max_retries=3):
            """Check if watcher is active; restart if not."""
            for attempt in range(max_retries):
                status = run(f"systemctl is-active {SERVICE_NAME}", check=False)
                if status == "active":
                    print("\n🟢 Watcher Status: ACTIVE ✅")
                    log.info("✅ Watcher service is active.")
                    print("──────────────────────────────────────────────")
                    print("📜 Recent Logs:")
                    print("──────────────────────────────────────────────")
                    logs = run(f"journalctl -u {SERVICE_NAME} -n 20 --no-pager", check=False)
                    print(logs if logs.strip() else "(No recent logs yet)")
                    print("──────────────────────────────────────────────")
                    return True

                # attempt restart if not active
                print(f"\n🔄 Attempt {attempt+1}: restarting watcher ({status}) ...")
                run(f"systemctl restart {SERVICE_NAME}", check=False)
                delay = min(5 * (2 ** attempt), 60)
                print(f"⏳ Waiting {delay}s for recovery...")
                time.sleep(delay)

            # after all retries
            final_status = run(f"systemctl is-active {SERVICE_NAME}", check=False)
            if final_status == "active":
                print("\n🟢 Watcher recovered after restart ✅")
                log.info("✅ Watcher recovered after restart.")
                return True
            else:
                print("\n🔴 Watcher failed to start after retries ❌")
                log.error("❌ Watcher did not recover after retries.")
                return False



def summarize(openai_key, report_path: Path = None):
    print("\n──────────────────────────────────────────────")
    print("🎉 HyperX Installation Summary")
    print("──────────────────────────────────────────────")
    print(f"📂 Base Directory: {BASE_DIR}")
    print(f"📄 Environment:    {HYPERX_ENV}")
    print(f"🔑 OpenAI Key:     {'✅ Found' if openai_key else '⚠️ Missing'}")
    print(f"⚙️  Service File:   {'✅ Found' if SERVICE_PATH.exists() else '❌ Missing'}")
    check_watcher_health()

    """Display and optionally export full audit summary."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "os": f"{platform.system()} {platform.release()}",
        "kernel": platform.version(),
        "python_version": platform.python_version(),
        "django_version": None,
        "hyperx_version": None,
        "env_file": str(HYPERX_ENV),
        "env_exists": HYPERX_ENV.exists(),
        "service_file": str(SERVICE_PATH),
        "service_exists": SERVICE_PATH.exists(),
        "watcher_script": str(WATCHER_SCRIPT),
        "watcher_exists": WATCHER_SCRIPT.exists(),
        "openai_key_present": bool(openai_key),
        "watcher_status": "unknown",
    }

    # Framework versions
    try:
        
        summary["django_version"] = django.get_version()
    except Exception:
        pass

    try:
        summary["hyperx_version"] = subprocess.getoutput(
            "pip show hyperx-htmx | grep Version | cut -d ' ' -f2"
        ).strip() or None
    except Exception:
        pass

    # Human-readable output
    print("\n──────────────────────────────────────────────")
    print("🧾 Environment & Audit Metadata")
    print("──────────────────────────────────────────────")
    for k, v in {
        "OS": summary["os"],
        "Python": summary["python_version"],
        "Django": summary["django_version"] or "(not detected)",
        "HyperX": summary["hyperx_version"] or "(not detected)",
        "Timestamp": summary["timestamp"],
    }.items():
        print(f"{k:<10}: {v}")

    for label, ok in [
        ("ENV File", summary["env_exists"]),
        ("Service File", summary["service_exists"]),
        ("Watcher Script", summary["watcher_exists"]),
    ]:
        print(f"📦 {label:<16} {'✅ OK' if ok else '❌ Missing'}")

    # Optional JSON report
    if report_path:
        report_data = {
            **summary,
            "validated": summary["env_exists"] and summary["service_exists"],
        }
        try:
            Path(report_path).write_text(json.dumps(report_data, indent=2))
            print(f"\n📄 JSON audit report saved to: {report_path}")
            log.info(f"Audit JSON exported → {report_path}")
        except Exception as e:
            print(f"❌ Failed to write report: {e}")
            log.error(f"Report write error: {e}")

    print("──────────────────────────────────────────────")
    print("💡 Verify: sudo systemctl status hyperx-dataset-watch")
    print("💡 Logs:   tail -f /var/log/hyperx_core_install.log")
    print("──────────────────────────────────────────────\n")
    log.info("✅ Installation and audit summary displayed.")


    def main():
        parser = argparse.ArgumentParser(description="Install HyperX into Django or system environment.")
        parser.add_argument("settings_path", nargs="?", help="Path to settings.py")
        parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
        parser.add_argument("--system-install", action="store_true", help="Install watcher & environment (root only)")
        parser.add_argument("--report", nargs="?", const="/var/log/hyperx_audit.json",
                            help="Export JSON audit summary (default: /var/log/hyperx_audit.json)")
        args = parser.parse_args()

        # ── System-level install ───────────────────
        if args.system_install:
            if os.geteuid() != 0:
                print("❌ Please run with sudo for system installation.")
                sys.exit(1)
            key = ensure_env()
            install_dataset_watcher()
            summarize(key, report_path=args.report)
            print("✅ System-level setup complete.")
            return

        # ── Django integration ─────────────────────
        settings_path = args.settings_path or find_django_settings()
        if not settings_path:
            print("❌ Could not locate settings.py")
            sys.exit(1)

        installer = HyperXInstaller(settings_path)
        ok = installer.install(create_backup=not args.no_backup)
        if ok:
            summarize(ensure_env(), report_path=args.report)
            print("\n🎯 Django integration complete.")
        else:
            print("❌ Installation failed.")



    if __name__ == "__main__":
        main()