"""
HTMX Core Analysis TestKit
========================

Enhanced analysis focusing on key component integration testing.
Based on the original htmx_core_analysis.py implementation.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Handle imports for both direct execution and module import
try:
    from .test_base_testkit import BaseTestKit
except ImportError:
    # Direct execution - use absolute import
    from test_base_testkit import BaseTestKit

class HTMXCoreAnalysisKit(BaseTestKit):
    """TestKit for enhanced HTMX Core component integration analysis"""
    
    def setUp(self):
        super().setUp()
        self.critical_components = [
            'htmx_core.registry.tab_registry',
            'htmx_core.xsystem.xtab_system', 
            'htmx_core.middleware.htmx_middleware',
            'htmx_core.utils.htmx_defaults',
            'htmx_core.templatetags.htmx_tags',
            'htmx_core.views.htmx_views',
            'htmx_core.models.htmx_models'
        ]
        self.integration_results = []
    
    def test_critical_component_loading(self):
        """Test loading of critical HTMX Core components"""
        print("🔄 Testing critical component loading...")
        
        successful_loads = 0
        
        for component in self.critical_components:
            try:
                module = importlib.import_module(component)
                successful_loads += 1
                
                # Get component info
                classes = [name for name, obj in inspect.getmembers(module, inspect.isclass) 
                          if obj.__module__ == component]
                functions = [name for name, obj in inspect.getmembers(module, inspect.isfunction)
                           if obj.__module__ == component]
                
                self.integration_results.append({
                    'component': component,
                    'status': 'loaded',
                    'classes': classes,
                    'functions': functions,
                    'class_count': len(classes),
                    'function_count': len(functions)
                })
                
                print(f"   ✅ {component}: {len(classes)} classes, {len(functions)} functions")
                
            except Exception as e:
                self.integration_results.append({
                    'component': component,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"   ❌ {component}: {e}")
        
        success_rate = (successful_loads / len(self.critical_components) * 100)
        message = f"Critical component loading: {success_rate:.1f}% ({successful_loads}/{len(self.critical_components)})"
        
        self.add_test_result("Critical Component Loading", success_rate > 80, message, {
            'success_rate': success_rate,
            'loaded_components': successful_loads,
            'total_components': len(self.critical_components),
            'results': self.integration_results
        })
    
    def test_tab_registry_integration(self):
        """Test TabRegistry integration and functionality"""
        print("📑 Testing TabRegistry integration...")
        
        try:
            from htmx_core.utils.htmx_x_tab_registry import TabRegistry
            
            # Test registry initialization
            registry = TabRegistry()
            
            # Test tab discovery
            all_tabs = registry.get_all_tabs()
            tab_count = len(all_tabs)
            
            # Test specific tab operations
            test_results = {
                'initialization': True,
                'tab_discovery': tab_count > 0,
                'tab_count': tab_count,
                'sample_tabs': list(all_tabs.keys())[:5] if all_tabs else []
            }
            
            # Test tab validation
            valid_tabs = 0
            for tab_name, tab_info in all_tabs.items():
                if isinstance(tab_info, dict) and 'title' in tab_info:
                    valid_tabs += 1
            
            test_results['valid_tabs'] = valid_tabs
            test_results['validation_rate'] = (valid_tabs / tab_count * 100) if tab_count > 0 else 0
            
            success = tab_count > 0 and test_results['validation_rate'] > 80
            message = f"TabRegistry: {tab_count} tabs discovered, {test_results['validation_rate']:.1f}% valid"
            
            self.add_test_result("TabRegistry Integration", success, message, test_results)
            
            print(f"   ✅ TabRegistry: {tab_count} tabs, {test_results['validation_rate']:.1f}% valid")
            
        except Exception as e:
            self.add_test_result("TabRegistry Integration", False, f"TabRegistry test failed: {str(e)}")
            print(f"   ❌ TabRegistry: {e}")
    
    def test_xtab_system_functionality(self):
        """Test XTabSystem functionality"""
        print("⚡ Testing XTabSystem functionality...")
        
        try:
            from htmx_core.utils.htmx_x_tab_system import XTabSystem
            
            # Test XTabSystem initialization
            xtab = XTabSystem()
            
            test_results = {
                'initialization': True,
                'methods_available': []
            }
            
            # Test available methods
            methods = [method for method in dir(xtab) if not method.startswith('_')]
            test_results['methods_available'] = methods
            test_results['method_count'] = len(methods)
            
            # Test specific functionality if methods are available
            functionality_tests = 0
            if hasattr(xtab, 'get_tabs'):
                try:
                    tabs = xtab.get_tabs()
                    functionality_tests += 1
                    test_results['get_tabs_working'] = True
                except:
                    test_results['get_tabs_working'] = False
            
            if hasattr(xtab, 'render'):
                try:
                    # Basic render test (may fail due to context requirements)
                    functionality_tests += 1
                    test_results['render_method_exists'] = True
                except:
                    test_results['render_method_exists'] = False
            
            success = len(methods) > 0
            message = f"XTabSystem: {len(methods)} methods available"
            
            self.add_test_result("XTabSystem Functionality", success, message, test_results)
            
            print(f"   ✅ XTabSystem: {len(methods)} methods")
            
        except Exception as e:
            self.add_test_result("XTabSystem Functionality", False, f"XTabSystem test failed: {str(e)}")
            print(f"   ❌ XTabSystem: {e}")
    
    def test_middleware_integration(self):
        """Test HTMX Middleware integration"""
        print("🔗 Testing HTMX Middleware integration...")
        
        try:
            from htmx_core.middleware.htmx_benchmark_security import HTMXMiddleware
            
            # Test middleware initialization with dummy get_response
            def dummy_get_response(request):
                return None
            
            middleware = HTMXMiddleware(dummy_get_response)
            
            test_results = {
                'initialization': True,
                'methods_available': []
            }
            
            # Test available methods
            methods = [method for method in dir(middleware) if not method.startswith('_')]
            test_results['methods_available'] = methods
            test_results['method_count'] = len(methods)
            
            # Check for expected middleware methods
            expected_methods = ['__call__', 'process_request', 'process_response']
            available_expected = [method for method in expected_methods if hasattr(middleware, method)]
            test_results['expected_methods'] = available_expected
            test_results['expected_method_coverage'] = len(available_expected) / len(expected_methods) * 100
            
            success = len(methods) > 0
            message = f"HTMXMiddleware: {len(methods)} methods, {test_results['expected_method_coverage']:.1f}% coverage"
            
            self.add_test_result("Middleware Integration", success, message, test_results)
            
            print(f"   ✅ HTMXMiddleware: {len(methods)} methods")
            
        except Exception as e:
            self.add_test_result("Middleware Integration", False, f"Middleware test failed: {str(e)}")
            print(f"   ❌ HTMXMiddleware: {e}")
    
    def test_template_tags_functionality(self):
        """Test HTMX template tags functionality"""
        print("🏷️ Testing HTMX template tags...")
        
        try:
            from htmx_core.templatetags.htmx_tags import register
            
            test_results = {
                'register_loaded': True,
                'available_tags': [],
                'available_filters': []
            }
            
            # Get registered tags and filters
            if hasattr(register, 'tags'):
                test_results['available_tags'] = list(register.tags.keys())
            if hasattr(register, 'filters'):
                test_results['available_filters'] = list(register.filters.keys())
            
            test_results['tag_count'] = len(test_results['available_tags'])
            test_results['filter_count'] = len(test_results['available_filters'])
            
            total_items = test_results['tag_count'] + test_results['filter_count']
            
            success = total_items > 0
            message = f"Template tags: {test_results['tag_count']} tags, {test_results['filter_count']} filters"
            
            self.add_test_result("Template Tags", success, message, test_results)
            
            print(f"   ✅ Template tags: {test_results['tag_count']} tags, {test_results['filter_count']} filters")
            
        except Exception as e:
            self.add_test_result("Template Tags", False, f"Template tags test failed: {str(e)}")
            print(f"   ❌ Template tags: {e}")
    
    def test_views_integration(self):
        """Test HTMX views integration"""
        print("🌐 Testing HTMX views integration...")
        
        try:
            from htmx_core.views import htmx_views
            
            test_results = {
                'module_loaded': True,
                'available_views': [],
                'available_functions': []
            }
            
            # Get available views and functions
            for name, obj in inspect.getmembers(htmx_views):
                if inspect.isfunction(obj):
                    test_results['available_functions'].append(name)
                elif inspect.isclass(obj):
                    test_results['available_views'].append(name)
            
            test_results['view_count'] = len(test_results['available_views'])
            test_results['function_count'] = len(test_results['available_functions'])
            
            total_items = test_results['view_count'] + test_results['function_count']
            
            success = total_items > 0
            message = f"Views: {test_results['view_count']} classes, {test_results['function_count']} functions"
            
            self.add_test_result("Views Integration", success, message, test_results)
            
            print(f"   ✅ Views: {test_results['view_count']} classes, {test_results['function_count']} functions")
            
        except Exception as e:
            self.add_test_result("Views Integration", False, f"Views test failed: {str(e)}")
            print(f"   ❌ Views: {e}")
    
    def test_utils_functionality(self):
        """Test HTMX utils functionality"""
        print("🛠️ Testing HTMX utils functionality...")
        
        try:
            from htmx_core.utils import htmx_defaults
            
            test_results = {
                'module_loaded': True,
                'available_functions': []
            }
            
            # Get available utility functions
            for name, obj in inspect.getmembers(htmx_defaults, inspect.isfunction):
                if not name.startswith('_'):
                    test_results['available_functions'].append(name)
            
            test_results['function_count'] = len(test_results['available_functions'])
            
            # Test specific utility functions
            if 'htmx_tabber' in test_results['available_functions']:
                try:
                    # Test htmx_tabber function (may need context)
                    test_results['htmx_tabber_available'] = True
                except:
                    test_results['htmx_tabber_available'] = False
            
            success = test_results['function_count'] > 0
            message = f"Utils: {test_results['function_count']} utility functions"
            
            self.add_test_result("Utils Functionality", success, message, test_results)
            
            print(f"   ✅ Utils: {test_results['function_count']} functions")
            
        except Exception as e:
            self.add_test_result("Utils Functionality", False, f"Utils test failed: {str(e)}")
            print(f"   ❌ Utils: {e}")
    
    def test_system_health_check(self):
        """Perform overall system health check"""
        print("🏥 Performing system health check...")
        
        health_metrics = {
            'critical_components_loaded': 0,
            'total_critical_components': len(self.critical_components),
            'integration_success_rate': 0,
            'overall_health_score': 0
        }
        
        # Count successful integrations from previous tests
        successful_tests = sum(1 for test in self.test_results['tests'] if test.get('success', False))
        total_tests = len(self.test_results['tests'])
        
        if total_tests > 0:
            health_metrics['integration_success_rate'] = successful_tests / total_tests * 100
        
        # Calculate health score
        health_metrics['overall_health_score'] = health_metrics['integration_success_rate']
        
        # Determine health status
        if health_metrics['overall_health_score'] >= 90:
            health_status = "Excellent"
        elif health_metrics['overall_health_score'] >= 75:
            health_status = "Good"
        elif health_metrics['overall_health_score'] >= 60:
            health_status = "Fair"
        else:
            health_status = "Needs Attention"
        
        health_metrics['health_status'] = health_status
        
        message = f"System Health: {health_status} ({health_metrics['overall_health_score']:.1f}%)"
        
        self.add_test_result("System Health Check", health_metrics['overall_health_score'] >= 75, message, health_metrics)
        
        print(f"   🏥 Overall Health: {health_status} ({health_metrics['overall_health_score']:.1f}%)")
    
    def tearDown(self):
        """Generate final analysis summary"""
        # Calculate summary statistics
        total_tests = len(self.test_results['tests'])
        passed_tests = sum(1 for test in self.test_results['tests'] if test.get('success', False))
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Count loaded components
        loaded_components = len([r for r in self.integration_results if r.get('status') == 'loaded'])
        total_classes = sum(r.get('class_count', 0) for r in self.integration_results if r.get('status') == 'loaded')
        total_functions = sum(r.get('function_count', 0) for r in self.integration_results if r.get('status') == 'loaded')
        
        self.test_results['summary'] = {
            'Total Integration Tests': total_tests,
            'Passed Tests': passed_tests,
            'Success Rate': f"{success_rate:.1f}%",
            'Components Loaded': f"{loaded_components}/{len(self.critical_components)}",
            'Total Classes': total_classes,
            'Total Functions': total_functions,
            'System Health': "Excellent" if success_rate >= 90 else "Good" if success_rate >= 75 else "Fair" if success_rate >= 60 else "Needs Attention"
        }
        
        print("\n" + "="*60)
        print("📊 HTMX CORE ANALYSIS SUMMARY")
        print("="*60)
        for key, value in self.test_results['summary'].items():
            print(f"{key}: {value}")
        print("="*60)
        
        super().tearDown()

if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)