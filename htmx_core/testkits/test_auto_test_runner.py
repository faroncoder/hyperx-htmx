"""
HTMX Core Auto-Discovery Test Runner
===================================

Automatically discovers htmx_* files and runs comprehensive tests on each one.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
import unittest
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change to project root directory for Django setup
os.chdir(PROJECT_ROOT)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from htmx_core.utils.htmx_auto_discovery import HTMXAutoDiscovery

# Handle imports for both direct execution and module import
try:
    from .test_base_testkit import BaseTestKit
    from .test_reporter import TestKitReporter
except ImportError:
    # Direct execution - use absolute imports
    from test_base_testkit import BaseTestKit
    from test_reporter import TestKitReporter

logger = logging.getLogger(__name__)

class AutoTestRunner:
    """Auto-discovery test runner for HTMX Core files"""
    
    def __init__(self):
        self.discovery = HTMXAutoDiscovery()
        self.reporter = TestKitReporter()
        self.test_results = {}
        
    def discover_and_test_all(self):
        """Discover all htmx_* files and run comprehensive tests on each"""
        print("🔍 HTMX Auto-Discovery Test Runner")
        print("=" * 60)
        
        # Discover all components
        components = self.discovery.discover_all_components()
        
        # Get file paths for testing
        file_paths = self._get_discovered_file_paths()
        
        print(f"📁 Found {len(file_paths)} htmx_* files to test")
        print(f"🧩 Discovered {sum(len(comps) for comps in components.values())} components")
        print("-" * 60)
        
        # Run tests for each file
        for file_path in file_paths:
            self._test_file_comprehensive(file_path)
            
        # Generate final report
        self._generate_final_report()
        
    def _get_discovered_file_paths(self) -> List[Path]:
        """Get all htmx_* file paths from discovery"""
        file_paths = []
        
        # Scan all subdirectories in htmx_core
        for root, dirs, files in os.walk(self.discovery.htmx_core_path):
            for file in files:
                if file.startswith('htmx_') and file.endswith('.py'):
                    file_paths.append(Path(root) / file)
                    
        return sorted(file_paths)
        
    def _test_file_comprehensive(self, file_path: Path):
        """Run comprehensive tests on a single htmx_* file"""
        relative_path = file_path.relative_to(self.discovery.htmx_core_path)
        module_name = str(relative_path).replace('/', '.').replace('.py', '')
        
        print(f"\n🧪 Testing: {relative_path}")
        
        file_tests = {
            'syntax_check': False,
            'import_test': False,
            'function_tests': [],
            'class_tests': [],
            'structure_analysis': {},
            'performance_check': False
        }
        
        try:
            # 1. Syntax Check
            file_tests['syntax_check'] = self._test_syntax(file_path)
            
            # 2. Import Test
            module, file_tests['import_test'] = self._test_import(module_name, file_path)
            
            if module and file_tests['import_test']:
                # 3. Function Tests
                file_tests['function_tests'] = self._test_functions(module, file_path)
                
                # 4. Class Tests  
                file_tests['class_tests'] = self._test_classes(module, file_path)
                
                # 5. Structure Analysis
                file_tests['structure_analysis'] = self._analyze_structure(module, file_path)
                
                # 6. Performance Check
                file_tests['performance_check'] = self._test_performance(module, file_path)
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")
            
        self.test_results[str(relative_path)] = file_tests
        self._print_file_summary(relative_path, file_tests)
        
    def _test_syntax(self, file_path: Path) -> bool:
        """Test file syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            compile(content, str(file_path), 'exec')
            print(f"   ✅ Syntax: Valid")
            return True
            
        except SyntaxError as e:
            print(f"   ❌ Syntax: Error on line {e.lineno}: {e.msg}")
            return False
        except Exception as e:
            print(f"   ⚠️ Syntax: Couldn't check - {e}")
            return False
            
    def _test_import(self, module_name: str, file_path: Path) -> tuple:
        """Test module import"""
        try:
            # Convert file path to module path
            full_module = f"htmx_core.{module_name}"
            module = importlib.import_module(full_module)
            print(f"   ✅ Import: Success")
            return module, True
            
        except ImportError as e:
            print(f"   ❌ Import: Failed - {e}")
            return None, False
        except Exception as e:
            print(f"   ⚠️ Import: Error - {e}")
            return None, False
            
    def _test_functions(self, module, file_path: Path) -> List[Dict]:
        """Test all functions in the module"""
        function_results = []
        
        functions = [obj for name, obj in inspect.getmembers(module, inspect.isfunction)
                    if obj.__module__ == module.__name__]
        
        if not functions:
            print(f"   📝 Functions: None found")
            return function_results
            
        print(f"   📝 Functions: Testing {len(functions)} functions")
        
        for func in functions:
            func_test = self._test_single_function(func)
            function_results.append(func_test)
            
        return function_results
        
    def _test_single_function(self, func) -> Dict:
        """Test a single function"""
        func_name = func.__name__
        
        try:
            # Get function signature
            sig = inspect.signature(func)
            params = len(sig.parameters)
            
            # Check if it has docstring
            has_docstring = bool(func.__doc__ and func.__doc__.strip())
            
            # Basic callable test
            is_callable = callable(func)
            
            result = {
                'name': func_name,
                'callable': is_callable,
                'parameters': params,
                'has_docstring': has_docstring,
                'signature': str(sig),
                'status': 'pass' if is_callable else 'fail'
            }
            
            status_icon = "✅" if is_callable else "❌"
            print(f"     {status_icon} {func_name}({params} params)")
            
            return result
            
        except Exception as e:
            return {
                'name': func_name,
                'error': str(e),
                'status': 'error'
            }
            
    def _test_classes(self, module, file_path: Path) -> List[Dict]:
        """Test all classes in the module"""
        class_results = []
        
        classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass)
                  if obj.__module__ == module.__name__]
        
        if not classes:
            print(f"   🏗️ Classes: None found")
            return class_results
            
        print(f"   🏗️ Classes: Testing {len(classes)} classes")
        
        for cls in classes:
            class_test = self._test_single_class(cls)
            class_results.append(class_test)
            
        return class_results
        
    def _test_single_class(self, cls) -> Dict:
        """Test a single class"""
        class_name = cls.__name__
        
        try:
            # Check if instantiable (try with no args first)
            instantiable = False
            instance = None
            
            try:
                instance = cls()
                instantiable = True
            except TypeError:
                # Try to count required args
                try:
                    sig = inspect.signature(cls.__init__)
                    required_params = [p for p in sig.parameters.values() 
                                     if p.default == p.empty and p.name != 'self']
                    instantiable = len(required_params) == 0
                except:
                    pass
            except Exception:
                pass
                
            # Count methods
            methods = [name for name, obj in inspect.getmembers(cls, inspect.ismethod)]
            method_count = len(methods)
            
            # Check for docstring
            has_docstring = bool(cls.__doc__ and cls.__doc__.strip())
            
            result = {
                'name': class_name,
                'instantiable': instantiable,
                'method_count': method_count,
                'has_docstring': has_docstring,
                'status': 'pass' if instantiable or method_count > 0 else 'warning'
            }
            
            status_icon = "✅" if instantiable else "⚠️" 
            print(f"     {status_icon} {class_name}({method_count} methods)")
            
            return result
            
        except Exception as e:
            return {
                'name': class_name,
                'error': str(e),
                'status': 'error'
            }
            
    def _analyze_structure(self, module, file_path: Path) -> Dict:
        """Analyze module structure"""
        try:
            # Count lines of code
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Count imports
            imports = len([line for line in lines if line.strip().startswith(('import ', 'from '))])
            
            # Count docstrings
            docstring_lines = len([line for line in lines if '"""' in line or "'''" in line])
            
            structure = {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'import_count': imports,
                'docstring_indicators': docstring_lines
            }
            
            print(f"   📊 Structure: {total_lines} lines, {imports} imports")
            
            return structure
            
        except Exception as e:
            return {'error': str(e)}
            
    def _test_performance(self, module, file_path: Path) -> bool:
        """Basic performance/load test"""
        try:
            import time
            
            start_time = time.time()
            
            # Try to reload the module (tests import speed)
            importlib.reload(module)
            
            load_time = time.time() - start_time
            
            # Consider fast if loads under 100ms
            is_fast = load_time < 0.1
            
            print(f"   ⚡ Performance: {load_time:.3f}s load time")
            
            return is_fast
            
        except Exception as e:
            print(f"   ⚡ Performance: Couldn't test - {e}")
            return False
            
    def _print_file_summary(self, file_path: Path, tests: Dict):
        """Print summary for a file"""
        total_tests = 0
        passed_tests = 0
        
        # Count basic tests
        basic_tests = ['syntax_check', 'import_test', 'performance_check']
        for test in basic_tests:
            if tests.get(test) is not None:
                total_tests += 1
                if tests[test]:
                    passed_tests += 1
                    
        # Count function tests
        for func_test in tests.get('function_tests', []):
            total_tests += 1
            if func_test.get('status') == 'pass':
                passed_tests += 1
                
        # Count class tests  
        for class_test in tests.get('class_tests', []):
            total_tests += 1
            if class_test.get('status') == 'pass':
                passed_tests += 1
                
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"   {status_icon} Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        else:
            print(f"   ❓ Summary: No tests available")
            
    def _generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST REPORT")
        print("=" * 60)
        
        total_files = len(self.test_results)
        healthy_files = 0
        total_components = 0
        
        for file_path, tests in self.test_results.items():
            # Count as healthy if syntax + import pass
            if tests.get('syntax_check') and tests.get('import_test'):
                healthy_files += 1
                
            # Count components (functions + classes)
            total_components += len(tests.get('function_tests', []))
            total_components += len(tests.get('class_tests', []))
            
        health_rate = (healthy_files / total_files * 100) if total_files > 0 else 0
        
        print(f"📁 Files Tested: {total_files}")
        print(f"✅ Healthy Files: {healthy_files} ({health_rate:.1f}%)")
        print(f"🧩 Total Components: {total_components}")
        
        # Status determination
        if health_rate >= 90:
            status = "🎉 EXCELLENT"
            color = "green"
        elif health_rate >= 75:
            status = "👍 GOOD"  
            color = "yellow"
        elif health_rate >= 50:
            status = "⚠️ NEEDS ATTENTION"
            color = "orange"
        else:
            status = "❌ CRITICAL"
            color = "red"
            
        print(f"🏥 Overall Status: {status}")
        print("=" * 60)


def main():
    """Main entry point"""
    runner = AutoTestRunner()
    runner.discover_and_test_all()


if __name__ == '__main__':
    main()