"""
TestKit Configuration
===================

Configuration settings for the TestKit framework.
"""

from pathlib import Path
import os

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
TESTKITS_ROOT = PROJECT_ROOT / 'testkits'
REPORTS_PATH = TESTKITS_ROOT / 'reports'
HTMX_CORE_PATH = PROJECT_ROOT / 'htmx_core'

# Django settings
DJANGO_SETTINGS_MODULE = 'config.settings'

# TestKit settings
DEFAULT_VERBOSITY = 2
MAX_REPORT_FILES = 50
REPORT_RETENTION_DAYS = 30

# File discovery settings
SKIP_DIRECTORIES = ['__pycache__', '.git', 'node_modules', 'staticfiles', '.pytest_cache']
SKIP_FILES = ['.DS_Store', '.gitignore', '*.pyc']

# Analysis settings
MIN_FILE_SIZE_FOR_ANALYSIS = 10  # bytes
MAX_IMPORT_DEPTH = 10

# Reporting settings
CHART_DPI = 300
CHART_SIZE = (15, 10)
DEFAULT_COLORS = {
    'success': '#4CAF50',
    'warning': '#FF9800', 
    'error': '#F44336',
    'info': '#2196F3',
    'purple': '#9C27B0'
}

# TestKit specific settings
DISCOVERY_KIT_SETTINGS = {
    'max_instantiation_attempts': 100,
    'function_param_limit': 5,
    'include_private_methods': False
}

ANALYSIS_KIT_SETTINGS = {
    'critical_success_threshold': 75,
    'health_score_weights': {
        'component_loading': 0.3,
        'integration_tests': 0.4,
        'functionality_tests': 0.3
    }
}

ORPHANED_FILES_SETTINGS = {
    'orphaned_threshold': 10,  # percentage
    'cleanup_confidence_threshold': 'medium',
    'auto_discovery_patterns': ['_tab_def.py', '_tabs.py', 'tab_config.py'],
    'django_standard_files': ['__init__.py', 'apps.py', 'admin.py', 'models.py', 'views.py', 'urls.py']
}

# Export settings
__all__ = [
    'PROJECT_ROOT',
    'TESTKITS_ROOT', 
    'REPORTS_PATH',
    'HTMX_CORE_PATH',
    'DEFAULT_VERBOSITY',
    'DISCOVERY_KIT_SETTINGS',
    'ANALYSIS_KIT_SETTINGS',
    'ORPHANED_FILES_SETTINGS'
]