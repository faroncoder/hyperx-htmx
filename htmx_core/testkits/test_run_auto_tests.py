#!/usr/bin/env python3
"""
Auto-Discovery Test Runner Script
================================

Runs comprehensive tests on all auto-discovered htmx_* files
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change to project root directory for Django setup
os.chdir(PROJECT_ROOT)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Import with absolute path when running directly
if __name__ == '__main__':
    # Add testkits directory to path for direct execution
    testkits_dir = Path(__file__).parent
    sys.path.insert(0, str(testkits_dir))
    from test_auto_test_runner import AutoTestRunner
else:
    from .test_auto_test_runner import AutoTestRunner

def main():
    """Run auto-discovery testing"""
    print("🚀 Starting HTMX Auto-Discovery Test Runner")
    print("=" * 60)
    
    runner = AutoTestRunner()
    runner.discover_and_test_all()
    
    print("\n🎉 Auto-Discovery Testing Complete!")

if __name__ == '__main__':
    main()