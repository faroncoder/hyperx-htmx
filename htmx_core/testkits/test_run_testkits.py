#!/usr/bin/env python3
"""
TestKit Quick Runner Script
=========================

Convenience script for quickly running TestKits.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change to project root directory for Django setup
os.chdir(PROJECT_ROOT)

# Handle imports for both direct execution and module import
try:
    from .test_runner import TestKitRunner
except ImportError:
    # Direct execution - add testkits directory to path
    testkits_dir = Path(__file__).parent
    sys.path.insert(0, str(testkits_dir))
    from test_runner import TestKitRunner

def main():
    """Quick runner main function"""
    runner = TestKitRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            runner.list_available_kits()
        elif command == 'all':
            runner.run_all()
        elif command in runner.available_kits:
            runner.run_kit(command)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: list, all, health, discovery, analysis, orphaned")
    else:
        print("🧪 S5Portal TestKits Quick Runner")
        print("================================")
        print("Usage:")
        print("  python run_testkits.py list      - List available TestKits")
        print("  python run_testkits.py all       - Run all TestKits")
        print("  python run_testkits.py health    - Run System Health TestKit")
        print("  python run_testkits.py discovery - Run Discovery TestKit")
        print("  python run_testkits.py analysis  - Run Analysis TestKit") 
        print("  python run_testkits.py orphaned  - Run Orphaned Files TestKit")

if __name__ == '__main__':
    main()