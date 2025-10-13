
from pathlib import Path
import shutil
import subprocess
from hyperx.bin.cli.utils.django_helper import *
from hyperx.bin.cli.generator import *
from hyperx.bin.cli.logger.hx_logger import *


_logger = load_logger("hyperx_install")
_logger.info("hyperx_install initialized")





def run_postinstall():
    """Post-install cleanup and guidance."""
    print("\n🧹 Cleaning management commands...")
    
    management_dir = Path(hyperx.__file__).parent / "management"
    if management_dir.exists():
        shutil.rmtree(management_dir)
        print("✅ Removed old management commands")
    print("\n🎯 HyperX ready to use!")




def run_install(settings_path=None, no_backup=False, force=False):
    """Perform HyperX installation and repository sync."""
    
    settings_path = find_django_settings() or find_settings_path()
    
    if not settings_path:
        print("❌ Could not find settings.py"); return

    


    
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(["git", "clone", repo, str(target)], check=True)
            print(f"✅ Cloned HyperX elements to {target}")
        except subprocess.CalledProcessError:
            print("⚠️ Failed to clone HyperX elements")
    print("🎉 HyperX installation complete!")
