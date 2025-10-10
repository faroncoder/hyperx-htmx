from pathlib import Path
import shutil, subprocess
from hyperx.bin.utils.django_helper import  find_settings_path
from hyperx.bin.cli.generator import find_django_settings



def run_install(settings_path=None, no_backup=False, force=False):
    """Perform HyperX installation and repository sync."""
    
    settings_path = find_django_settings() or find_settings_path()
    
    if not settings_path:
        print("❌ Could not find settings.py"); return

    repo = "https://github.com/faroncoder/hyperx-elements.git"
    target = Path.home() / "hyperx" / "core" / "hyperx_elements"


    if target.exists():
        shutil.rmtree(target)
    try:
        subprocess.run(["git", "clone", repo, str(target)], check=True)
        print(f"✅ Cloned HyperX elements to {target}")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to clone HyperX elements")
    print("🎉 HyperX installation complete!")