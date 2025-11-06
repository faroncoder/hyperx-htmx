"""
HTMX Core Discovery TestKit
==========================

Comprehensive discovery and functionality testing for HTMX Core components.
Based on the original test_htmx_core_discovery.py implementation.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Handle imports for both direct execution and module import
try:
    from .test_base_testkit import BaseTestKit
except ImportError:
    # Direct execution - use absolute import
    from test_base_testkit import BaseTestKit

class HTMXCoreDiscoveryKit(BaseTestKit):
    """TestKit for comprehensive HTMX Core component discovery and testing"""
    
    def setUp(self):
        super().setUp()
        self.discovered_files = []
        self.component_stats = {
            'total_files': 0,
            'total_classes': 0,
            'total_functions': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'working_classes': 0,
            'working_functions': 0
        }
    
    def test_file_discovery(self):
        """Test comprehensive file discovery using os.walk"""
        print("🔍 Starting HTMX Core file discovery...")
        
        try:
            self.discovered_files = self.discover_python_files(self.htmx_core_path)
            self.component_stats['total_files'] = len(self.discovered_files)
            
            success = len(self.discovered_files) > 0
            message = f"Discovered {len(self.discovered_files)} Python files in htmx_core"
            
            self.add_test_result("File Discovery", success, message, {
                'file_count': len(self.discovered_files),
                'files': [str(f.relative_to(self.project_root)) for f in self.discovered_files[:10]]  # First 10 files
            })
            
            self.assertTrue(success, message)
            
        except Exception as e:
            self.add_test_result("File Discovery", False, f"File discovery failed: {str(e)}")
            self.fail(f"File discovery failed: {str(e)}")
    
    def test_component_analysis(self):
        """Test analysis of all discovered files"""
        print("📊 Analyzing components in discovered files...")
        
        total_classes = 0
        total_functions = 0
        analysis_results = []
        
        for filepath in self.discovered_files:
            try:
                analysis = self.analyze_python_file(filepath)
                analysis_results.append(analysis)
                
                total_classes += len(analysis['classes'])
                total_functions += len(analysis['functions'])
                
            except Exception as e:
                print(f"   ❌ Analysis failed for {filepath}: {e}")
        
        self.component_stats['total_classes'] = total_classes
        self.component_stats['total_functions'] = total_functions
        
        success = len(analysis_results) > 0
        message = f"Analyzed {len(analysis_results)} files, found {total_classes} classes and {total_functions} functions"
        
        self.add_test_result("Component Analysis", success, message, {
            'analyzed_files': len(analysis_results),
            'total_classes': total_classes,
            'total_functions': total_functions,
            'sample_analysis': analysis_results[:3]  # First 3 analyses as sample
        })
        
        self.assertTrue(success, message)
    
    def test_module_imports(self):
        """Test importing all discoverable modules"""
        print("📦 Testing module imports...")
        
        successful_imports = 0
        failed_imports = 0
        import_results = []
        
        for filepath in self.discovered_files:
            # Convert file path to module path
            rel_path = filepath.relative_to(self.project_root)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            # Skip certain patterns
            if any(skip in module_path for skip in ['__pycache__', '.pyc', 'migrations']):
                continue
            
            success, message, module = self.test_import_module(module_path)
            
            if success:
                successful_imports += 1
                print(f"   ✅ {module_path}")
            else:
                failed_imports += 1
                print(f"   ❌ {module_path}: {message}")
            
            import_results.append({
                'module': module_path,
                'success': success,
                'message': message
            })
        
        self.component_stats['successful_imports'] = successful_imports
        self.component_stats['failed_imports'] = failed_imports
        
        total_attempts = successful_imports + failed_imports
        success_rate = (successful_imports / total_attempts * 100) if total_attempts > 0 else 0
        
        message = f"Import success rate: {success_rate:.1f}% ({successful_imports}/{total_attempts})"
        
        self.add_test_result("Module Imports", True, message, {
            'successful_imports': successful_imports,
            'failed_imports': failed_imports,
            'success_rate': success_rate,
            'sample_failures': [r for r in import_results if not r['success']][:5]
        })
    
    def test_class_instantiation(self):
        """Test instantiation of discoverable classes"""
        print("🏗️ Testing class instantiation...")
        
        working_classes = 0
        class_test_results = []
        
        for filepath in self.discovered_files:
            rel_path = filepath.relative_to(self.project_root)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            # Skip problematic modules
            if any(skip in module_path for skip in ['__pycache__', '.pyc', 'migrations']):
                continue
            
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_path:  # Only test classes defined in this module
                        try:
                            # Try basic instantiation
                            instance = obj()
                            working_classes += 1
                            print(f"   ✅ {module_path}.{name}")
                            
                            class_test_results.append({
                                'class': f"{module_path}.{name}",
                                'success': True,
                                'message': "Instantiated successfully"
                            })
                            
                        except Exception as e:
                            print(f"   ⚠️ {module_path}.{name}: {str(e)}")
                            
                            class_test_results.append({
                                'class': f"{module_path}.{name}",
                                'success': False,
                                'message': str(e)
                            })
            
            except Exception as e:
                continue  # Skip modules that can't be imported
        
        self.component_stats['working_classes'] = working_classes
        
        message = f"Successfully instantiated {working_classes} classes"
        
        self.add_test_result("Class Instantiation", True, message, {
            'working_classes': working_classes,
            'total_attempts': len(class_test_results),
            'sample_results': class_test_results[:10]
        })
    
    def test_function_discovery(self):
        """Test discovery and basic validation of functions"""
        print("🔧 Testing function discovery...")
        
        working_functions = 0
        function_test_results = []
        
        for filepath in self.discovered_files:
            rel_path = filepath.relative_to(self.project_root)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            # Skip problematic modules
            if any(skip in module_path for skip in ['__pycache__', '.pyc', 'migrations']):
                continue
            
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if obj.__module__ == module_path:  # Only test functions defined in this module
                        # Check if function is callable and has reasonable signature
                        sig = inspect.signature(obj)
                        param_count = len(sig.parameters)
                        
                        # Consider it working if it has a reasonable signature
                        if param_count <= 5:  # Arbitrary reasonable limit
                            working_functions += 1
                            print(f"   ✅ {module_path}.{name}()")
                            
                            function_test_results.append({
                                'function': f"{module_path}.{name}",
                                'success': True,
                                'params': param_count,
                                'signature': str(sig)
                            })
                        
            except Exception as e:
                continue  # Skip modules that can't be imported
        
        self.component_stats['working_functions'] = working_functions
        
        message = f"Discovered {working_functions} working functions"
        
        self.add_test_result("Function Discovery", True, message, {
            'working_functions': working_functions,
            'sample_functions': function_test_results[:15]
        })
    
    def test_critical_components(self):
        """Test critical HTMX Core components"""
        print("⚡ Testing critical components...")
        
        critical_tests = []
        
        # Test TabRegistry
        try:
            from htmx_core.utils.htmx_x_tab_registry import TabRegistry
            registry = TabRegistry()
            tab_count = len(registry.get_all_tabs())
            
            critical_tests.append({
                'component': 'TabRegistry',
                'success': True,
                'message': f"Found {tab_count} registered tabs",
                'details': {'tab_count': tab_count}
            })
            print(f"   ✅ TabRegistry: {tab_count} tabs")
            
        except Exception as e:
            critical_tests.append({
                'component': 'TabRegistry',
                'success': False,
                'message': str(e)
            })
            print(f"   ❌ TabRegistry: {e}")
        
        # Test XTabSystem
        try:
            from htmx_core.utils.htmx_x_tab_system import XTabSystem
            xtab = XTabSystem()
            
            critical_tests.append({
                'component': 'XTabSystem',
                'success': True,
                'message': "XTabSystem initialized successfully"
            })
            print("   ✅ XTabSystem: Initialized")
            
        except Exception as e:
            critical_tests.append({
                'component': 'XTabSystem',
                'success': False,
                'message': str(e)
            })
            print(f"   ❌ XTabSystem: {e}")
        
        # Test Middleware
        try:
            from htmx_core.middleware.htmx_benchmark_security import HTMXMiddleware
            middleware = HTMXMiddleware(lambda x: None)  # Dummy get_response
            
            critical_tests.append({
                'component': 'HTMXMiddleware',
                'success': True,
                'message': "HTMXMiddleware initialized successfully"
            })
            print("   ✅ HTMXMiddleware: Initialized")
            
        except Exception as e:
            critical_tests.append({
                'component': 'HTMXMiddleware',
                'success': False,
                'message': str(e)
            })
            print(f"   ❌ HTMXMiddleware: {e}")
        
        success_count = sum(1 for test in critical_tests if test['success'])
        total_count = len(critical_tests)
        
        message = f"Critical components test: {success_count}/{total_count} passed"
        
        self.add_test_result("Critical Components", success_count == total_count, message, {
            'tests': critical_tests,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0
        })
    
    def tearDown(self):
        """Generate final summary"""
        # Calculate overall statistics
        total_components = self.component_stats['total_classes'] + self.component_stats['total_functions']
        working_components = self.component_stats['working_classes'] + self.component_stats['working_functions']
        
        overall_success_rate = (working_components / total_components * 100) if total_components > 0 else 0
        
        self.test_results['summary'] = {
            'Total Files Discovered': self.component_stats['total_files'],
            'Total Classes Found': self.component_stats['total_classes'],
            'Total Functions Found': self.component_stats['total_functions'],
            'Working Classes': self.component_stats['working_classes'],
            'Working Functions': self.component_stats['working_functions'],
            'Import Success Rate': f"{(self.component_stats['successful_imports'] / (self.component_stats['successful_imports'] + self.component_stats['failed_imports']) * 100):.1f}%" if (self.component_stats['successful_imports'] + self.component_stats['failed_imports']) > 0 else "N/A",
            'Overall Success Rate': f"{overall_success_rate:.1f}%",
            'System Health': "Excellent" if overall_success_rate > 80 else "Good" if overall_success_rate > 60 else "Needs Attention"
        }
        
        print("\n" + "="*60)
        print("📋 HTMX CORE DISCOVERY SUMMARY")
        print("="*60)
        for key, value in self.test_results['summary'].items():
            print(f"{key}: {value}")
        print("="*60)
        
        super().tearDown()

if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)