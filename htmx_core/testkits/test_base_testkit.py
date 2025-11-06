"""
Base TestKit Class - Foundation for all TestKits
===============================================

Provides common functionality and structure for all TestKit implementations.
"""

import os
import sys
import unittest
import importlib
import inspect
import ast
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class BaseTestKit(unittest.TestCase):
    """Base class for all TestKit implementations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_root = PROJECT_ROOT
        self.htmx_core_path = self.project_root / 'htmx_core'
        self.reports_path = self.project_root / 'testkits' / 'reports'
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def setUp(self):
        """Set up test environment"""
        self.start_time = datetime.now()
        self.test_results = {
            'kit_name': self.__class__.__name__,
            'start_time': self.start_time.isoformat(),
            'tests': [],
            'summary': {}
        }
        
        # Ensure reports directory exists
        os.makedirs(self.reports_path, exist_ok=True)
        
        # Set up Django environment
        self._setup_django_environment()
    
    def tearDown(self):
        """Clean up after tests"""
        self.end_time = datetime.now()
        self.test_results['end_time'] = self.end_time.isoformat()
        self.test_results['duration'] = str(self.end_time - self.start_time)
        
        # Generate report
        self._generate_report()
    
    def _setup_django_environment(self):
        """Set up Django environment for testing"""
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            import django
            django.setup()
        except Exception as e:
            self.test_results['django_setup_error'] = str(e)
    
    def _generate_report(self):
        """Generate test report"""
        report_filename = f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.reports_path / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Also generate markdown report
        self._generate_markdown_report(report_path.with_suffix('.md'))
    
    def _generate_markdown_report(self, filepath: Path):
        """Generate markdown report"""
        with open(filepath, 'w') as f:
            f.write(f"# {self.test_results['kit_name']} Report\n\n")
            f.write(f"**Generated:** {self.test_results['end_time']}\n")
            f.write(f"**Duration:** {self.test_results['duration']}\n\n")
            
            if 'summary' in self.test_results:
                f.write("## Summary\n\n")
                for key, value in self.test_results['summary'].items():
                    f.write(f"- **{key}:** {value}\n")
            
            f.write("\n## Test Results\n\n")
            for test in self.test_results.get('tests', []):
                status = "✅" if test.get('success', False) else "❌"
                f.write(f"{status} **{test.get('name', 'Unknown')}**\n")
                if test.get('message'):
                    f.write(f"   - {test['message']}\n")
                f.write("\n")
    
    def add_test_result(self, name: str, success: bool, message: str = "", details: Dict = None):
        """Add a test result to the collection"""
        result = {
            'name': name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if details:
            result['details'] = details
            
        self.test_results['tests'].append(result)
    
    def discover_python_files(self, path: Path, pattern: str = "*.py") -> List[Path]:
        """Discover Python files using os.walk"""
        python_files = []
        for root, dirs, files in os.walk(path):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def analyze_python_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a Python file using AST"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(filepath))
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
            
            return {
                'filepath': str(filepath),
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'lines': len(content.splitlines()),
                'size': len(content)
            }
            
        except Exception as e:
            return {
                'filepath': str(filepath),
                'error': str(e),
                'classes': [],
                'functions': [],
                'imports': [],
                'lines': 0,
                'size': 0
            }
    
    def test_import_module(self, module_path: str) -> Tuple[bool, str, Any]:
        """Test importing a module"""
        try:
            module = importlib.import_module(module_path)
            return True, f"Successfully imported {module_path}", module
        except Exception as e:
            return False, f"Failed to import {module_path}: {str(e)}", None
    
    def test_class_instantiation(self, cls, *args, **kwargs) -> Tuple[bool, str, Any]:
        """Test class instantiation"""
        try:
            instance = cls(*args, **kwargs)
            return True, f"Successfully instantiated {cls.__name__}", instance
        except Exception as e:
            return False, f"Failed to instantiate {cls.__name__}: {str(e)}", None
    
    def test_function_call(self, func, *args, **kwargs) -> Tuple[bool, str, Any]:
        """Test function call"""
        try:
            result = func(*args, **kwargs)
            return True, f"Successfully called {func.__name__}", result
        except Exception as e:
            return False, f"Failed to call {func.__name__}: {str(e)}", None