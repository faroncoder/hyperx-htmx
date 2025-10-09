from pathlib import Path
import shutil, subprocess
from hyperx.core.core import find_django_settings, HyperXInstaller

def run_install(settings_path=None, no_backup=False, force=False):
    """Perform HyperX installation and repository sync."""
    settings_path = settings_path or find_django_settings()
    if not settings_path:
        print("❌ Could not find settings.py"); return

    repo = "https://github.com/faroncoder/hyperx-elements.git"
    target = Path("/hyperx/core/hyperx_elements")

    if target.exists():
        shutil.rmtree(target)
    subprocess.run(["git", "clone", repo, str(target)], check=True)

    installer = HyperXInstaller(settings_path)
    success = installer.install(create_backup=not no_backup)
    if success:
        print("✅ Installation complete!")
    else:
        print("⚠️ Installation failed")
