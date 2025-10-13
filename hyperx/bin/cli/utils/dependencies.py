import importlib.metadata
from packaging import version
import subprocess, sys, os, re, json, hmac, hashlib
from pathlib import Path




def check_and_install(reqs):
    to_install = {}
    for pkg, min_ver in reqs.items():
        try:
            current_ver = importlib.metadata.version(pkg)
            if version.parse(current_ver) < version.parse(min_ver):
                to_install[pkg] = min_ver
                print(f"🔄 {pkg} {current_ver} < {min_ver}  -> will update")
            else:
                print(f"✅ {pkg} {current_ver} (ok)")
        except importlib.metadata.PackageNotFoundError:
            to_install[pkg] = min_ver
            print(f"❌ {pkg} not found  -> will install")

    if to_install:
        print("\n📦 Installing missing / outdated packages:")
        args = [sys.executable, "-m", "pip", "install"] + [f"{p}>={v}" for p,v in to_install.items()]
        subprocess.run(args, check=True)
    else:
        print("\n🎉 All required packages already satisfied.")

check_and_install(REQUIRED)

