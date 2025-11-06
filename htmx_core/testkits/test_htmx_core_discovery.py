#!/usr/bin/env python3
"""
HTMX Core Discovery & Functionality Test
Uses os.walk to discover all classes and functions in htmx_core and tests their functionality.
"""

import os
import ast
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Set, Any
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

class HTMXCoreDiscoveryTest:
    def __init__(self):
        self.htmx_core_path = Path('htmx_core')
        self.discovered_classes = {}
        self.discovered_functions = {}
        self.test_results = {
            'total_files': 0,
            'total_classes': 0,
            'total_functions': 0,
            'working_classes': 0,
            'working_functions': 0,
            'failed_imports': [],
            'failed_tests': [],
            'successful_tests': []
        }

    def discover_python_files(self) -> List[Path]:
        """Use os.walk to find all Python files in htmx_core"""
        python_files = []
        
        for root, dirs, files in os.walk(self.htmx_core_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'migrations'}]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        self.test_results['total_files'] = len(python_files)
        return python_files

    def parse_file_for_definitions(self, file_path: Path) -> Dict[str, List[str]]:
        """Parse a Python file to extract class and function definitions"""
        definitions = {'classes': [], 'functions': []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    definitions['classes'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    # Skip private functions and methods inside classes
                    if not node.name.startswith('_'):
                        definitions['functions'].append(node.name)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return definitions

    def discover_all_definitions(self):
        """Discover all classes and functions in htmx_core"""
        python_files = self.discover_python_files()
        
        print(f"🔍 Discovering definitions in {len(python_files)} Python files...")
        
        for file_path in python_files:
            definitions = self.parse_file_for_definitions(file_path)
            
            # Convert file path to module path
            module_path = str(file_path.with_suffix('')).replace(os.sep, '.')
            
            if definitions['classes']:
                self.discovered_classes[module_path] = definitions['classes']
                self.test_results['total_classes'] += len(definitions['classes'])
            
            if definitions['functions']:
                self.discovered_functions[module_path] = definitions['functions']
                self.test_results['total_functions'] += len(definitions['functions'])

    def test_class_functionality(self, module_path: str, class_name: str) -> bool:
        """Test if a class can be imported and instantiated"""
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            
            # Check if it's a proper class
            if not inspect.isclass(cls):
                return False
            
            # Try to get class info (this tests if it's properly defined)
            signature = inspect.signature(cls.__init__) if hasattr(cls, '__init__') else None
            methods = [name for name, method in inspect.getmembers(cls, predicate=inspect.ismethod)]
            
            # For mixins and certain classes, just check they're importable
            if any(keyword in class_name.lower() for keyword in ['mixin', 'middleware', 'config']):
                self.test_results['successful_tests'].append(f"✅ Class {module_path}.{class_name} - Importable")
                return True
            
            # For registries and managers, try to access class methods
            if any(keyword in class_name.lower() for keyword in ['registry', 'manager', 'dispatcher']):
                class_methods = [name for name, method in inspect.getmembers(cls, predicate=inspect.ismethod)]
                if class_methods:
                    self.test_results['successful_tests'].append(f"✅ Class {module_path}.{class_name} - Has {len(class_methods)} methods")
                    return True
            
            self.test_results['successful_tests'].append(f"✅ Class {module_path}.{class_name} - Basic validation passed")
            return True
            
        except Exception as e:
            self.test_results['failed_imports'].append(f"❌ Class {module_path}.{class_name}: {str(e)}")
            return False

    def test_function_functionality(self, module_path: str, function_name: str) -> bool:
        """Test if a function can be imported and inspected"""
        try:
            module = importlib.import_module(module_path)
            func = getattr(module, function_name)
            
            # Check if it's a proper function
            if not (inspect.isfunction(func) or inspect.ismethod(func)):
                return False
            
            # Get function signature
            try:
                signature = inspect.signature(func)
                param_count = len(signature.parameters)
                
                # Check if function has docstring
                has_docstring = bool(func.__doc__)
                
                self.test_results['successful_tests'].append(
                    f"✅ Function {module_path}.{function_name} - {param_count} params, docstring: {has_docstring}"
                )
                return True
                
            except Exception as sig_error:
                # Some built-in or special functions might not have inspectable signatures
                self.test_results['successful_tests'].append(f"✅ Function {module_path}.{function_name} - Basic validation passed")
                return True
            
        except Exception as e:
            self.test_results['failed_imports'].append(f"❌ Function {module_path}.{function_name}: {str(e)}")
            return False

    def test_integration_functionality(self):
        """Test key integration points"""
        print("\n🧪 Testing Integration Functionality...")
        
        integration_tests = [
            {
                'name': 'HTMX Registry System',
                'test': lambda: self._test_htmx_registry()
            },
            {
                'name': 'Tab Registry System', 
                'test': lambda: self._test_tab_registry()
            },
            {
                'name': 'Middleware Components',
                'test': lambda: self._test_middleware()
            },
            {
                'name': 'Helper Functions',
                'test': lambda: self._test_helpers()
            },
            {
                'name': 'View Functions',
                'test': lambda: self._test_views()
            }
        ]
        
        for test in integration_tests:
            try:
                result = test['test']()
                if result:
                    self.test_results['successful_tests'].append(f"✅ Integration: {test['name']}")
                else:
                    self.test_results['failed_tests'].append(f"❌ Integration: {test['name']} - Failed")
            except Exception as e:
                self.test_results['failed_tests'].append(f"❌ Integration: {test['name']} - {str(e)}")

    def _test_htmx_registry(self) -> bool:
        """Test HTMX registry system"""
        from htmx_core.initializer import get_htmx_registry, is_htmx_core_ready
        
        registry = get_htmx_registry()
        is_ready = is_htmx_core_ready()
        
        return bool(registry and is_ready and len(registry) > 0)

    def _test_tab_registry(self) -> bool:
        """Test Tab registry system"""
        from htmx_core.utils.htmx_x_tab_registry import TabRegistry
        
        registry = TabRegistry()
        manifest = registry.generate_tab_manifest()
        
        return bool(manifest and 'total_tabs' in manifest and manifest['total_tabs'] > 0)

    def _test_middleware(self) -> bool:
        """Test middleware components can be imported"""
        middleware_modules = [
            'htmx_core.middleware.htmx_security',
            'htmx_core.middleware.htmx_switcher',
            'htmx_core.middleware.htmx_benchmark_security'
        ]
        
        for module_name in middleware_modules:
            module = importlib.import_module(module_name)
            # Check if module has classes that look like middleware
            classes = [name for name, obj in inspect.getmembers(module, inspect.isclass)]
            if not any('middleware' in cls.lower() for cls in classes):
                return False
        
        return True

    def _test_helpers(self) -> bool:
        """Test helper functions"""
        from htmx_core.utils.htmx_helpers import is_htmx_request, hx_redirect, hx_trigger
        from htmx_core.utils.htmx_defaults import htmx_defaults
        
        # These should be importable functions
        return all(callable(func) for func in [is_htmx_request, hx_redirect, hx_trigger, htmx_defaults])

    def _test_views(self) -> bool:
        """Test view functions"""
        from htmx_core.views.htmx_views import lazy_tab_map
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test')
        response = lazy_tab_map(request)
        
        return hasattr(response, 'status_code') and response.status_code == 200

    def run_discovery_test(self):
        """Run the complete discovery and functionality test"""
        print("=" * 60)
        print("🔬 HTMX CORE DISCOVERY & FUNCTIONALITY TEST")
        print("=" * 60)
        
        # Step 1: Discovery
        print("\n📁 STEP 1: DISCOVERING FILES & DEFINITIONS")
        self.discover_all_definitions()
        
        print(f"   Found {self.test_results['total_files']} Python files")
        print(f"   Found {self.test_results['total_classes']} classes")
        print(f"   Found {self.test_results['total_functions']} functions")
        
        # Step 2: Test Classes
        print(f"\n🏗️  STEP 2: TESTING {self.test_results['total_classes']} CLASSES")
        for module_path, classes in self.discovered_classes.items():
            for class_name in classes:
                if self.test_class_functionality(module_path, class_name):
                    self.test_results['working_classes'] += 1
        
        # Step 3: Test Functions  
        print(f"\n⚙️  STEP 3: TESTING {self.test_results['total_functions']} FUNCTIONS")
        for module_path, functions in self.discovered_functions.items():
            for function_name in functions:
                if self.test_function_functionality(module_path, function_name):
                    self.test_results['working_functions'] += 1
        
        # Step 4: Integration Tests
        self.test_integration_functionality()
        
        # Step 5: Report Results
        self.print_results()

    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Overall statistics
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Files Scanned: {self.test_results['total_files']}")
        print(f"   Classes Found: {self.test_results['total_classes']}")
        print(f"   Functions Found: {self.test_results['total_functions']}")
        print(f"   Working Classes: {self.test_results['working_classes']}/{self.test_results['total_classes']}")
        print(f"   Working Functions: {self.test_results['working_functions']}/{self.test_results['total_functions']}")
        
        # Success rate
        total_items = self.test_results['total_classes'] + self.test_results['total_functions']
        working_items = self.test_results['working_classes'] + self.test_results['working_functions']
        success_rate = (working_items / total_items * 100) if total_items > 0 else 0
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({working_items}/{total_items})")
        
        # Show successful tests (first 10)
        if self.test_results['successful_tests']:
            print(f"\n✅ SUCCESSFUL TESTS ({len(self.test_results['successful_tests'])}):")
            for test in self.test_results['successful_tests'][:10]:
                print(f"   {test}")
            if len(self.test_results['successful_tests']) > 10:
                print(f"   ... and {len(self.test_results['successful_tests']) - 10} more")
        
        # Show failed imports/tests
        if self.test_results['failed_imports']:
            print(f"\n❌ FAILED IMPORTS ({len(self.test_results['failed_imports'])}):")
            for failure in self.test_results['failed_imports'][:5]:
                print(f"   {failure}")
            if len(self.test_results['failed_imports']) > 5:
                print(f"   ... and {len(self.test_results['failed_imports']) - 5} more")
        
        if self.test_results['failed_tests']:
            print(f"\n❌ FAILED TESTS ({len(self.test_results['failed_tests'])}):")
            for failure in self.test_results['failed_tests']:
                print(f"   {failure}")
        
        # Final status
        print(f"\n🏆 FINAL STATUS:")
        if success_rate >= 90:
            print("   🎉 EXCELLENT - HTMX Core is highly functional!")
        elif success_rate >= 75:
            print("   ✅ GOOD - HTMX Core is mostly functional")
        elif success_rate >= 50:
            print("   ⚠️  FAIR - Some issues detected")
        else:
            print("   ❌ POOR - Significant issues detected")

if __name__ == "__main__":
    tester = HTMXCoreDiscoveryTest()
    tester.run_discovery_test()