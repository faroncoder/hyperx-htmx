from pathlib import Path
import shutil

def run_postinstall():
    """Post-install cleanup and guidance."""
    print("\n🧹 Cleaning management commands...")
    
    management_dir = Path(hyperx.__file__).parent / "management"
    if management_dir.exists():
        shutil.rmtree(management_dir)
        print("✅ Removed old management commands")
    print("\n🎯 HyperX ready to use!")

