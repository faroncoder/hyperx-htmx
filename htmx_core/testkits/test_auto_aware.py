"""
HTMX Core Auto-Aware Testing System
===================================

Automatically discovers and runs all TestKit files in the testkits directory.
Provides comprehensive results for dashboard integration and periodic monitoring.
"""

import os
import sys
import json
import time
import unittest
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import traceback

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change to project root directory for Django setup
os.chdir(PROJECT_ROOT)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Handle imports with fallback
try:
    from .test_base_testkit import BaseTestKit
    from .test_reporter import TestKitReporter
except ImportError:
    from test_base_testkit import BaseTestKit
    from test_reporter import TestKitReporter

class AutoAwareTestSystem:
    """Auto-discovery and execution system for all TestKits"""
    
    def __init__(self):
        self.testkits_path = Path(__file__).parent
        self.reports_path = self.testkits_path / 'reports'
        self.reports_path.mkdir(exist_ok=True)
        
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'discovered_tests': {},
            'execution_results': {},
            'summary': {},
            'dashboard_data': {}
        }
        
        self.discovered_test_files = []
        self.available_testkits = []
        
    def discover_all_test_files(self) -> List[Path]:
        """Discover all test_*.py files in testkits directory"""
        print("🔍 Auto-discovering TestKit files...")
        
        test_files = []
        
        # Walk through testkits directory
        for root, dirs, files in os.walk(self.testkits_path):
            # Skip __pycache__ and reports directories
            dirs[:] = [d for d in dirs if not d.startswith('__pycache__') and d != 'reports']
            
            for file in files:
                if file.startswith('test_') and file.endswith('.py') and file != 'test_auto_aware.py':
                    file_path = Path(root) / file
                    test_files.append(file_path)
                    
        self.discovered_test_files = sorted(test_files)
        print(f"   📁 Found {len(test_files)} TestKit files")
        
        return self.discovered_test_files
        
    def analyze_test_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a test file to extract TestKit classes and methods"""
        relative_path = file_path.relative_to(self.testkits_path)
        
        analysis = {
            'file_path': str(relative_path),
            'file_name': file_path.name,
            'module_name': file_path.stem,
            'test_classes': [],
            'test_methods': [],
            'importable': False,
            'analysis_time': time.time()
        }
        
        try:
            # Try to import the module
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            analysis['importable'] = True
            
            # Find TestKit classes
            for name in dir(module):
                obj = getattr(module, name)
                
                if (isinstance(obj, type) and 
                    issubclass(obj, unittest.TestCase) and 
                    obj != unittest.TestCase and 
                    obj != BaseTestKit):
                    
                    class_info = {
                        'class_name': name,
                        'test_methods': [],
                        'is_testkit': issubclass(obj, BaseTestKit) if BaseTestKit else False
                    }
                    
                    # Find test methods
                    for method_name in dir(obj):
                        if method_name.startswith('test_'):
                            method = getattr(obj, method_name)
                            if callable(method):
                                class_info['test_methods'].append({
                                    'method_name': method_name,
                                    'docstring': getattr(method, '__doc__', '').strip() if hasattr(method, '__doc__') else ''
                                })
                                
                    analysis['test_classes'].append(class_info)
                    analysis['test_methods'].extend(class_info['test_methods'])
                    
        except Exception as e:
            analysis['import_error'] = str(e)
            analysis['traceback'] = traceback.format_exc()
            
        return analysis
        
    def run_testkit_class(self, file_path: Path, class_name: str) -> Dict[str, Any]:
        """Run a specific TestKit class and collect results"""
        print(f"   🧪 Running {class_name} from {file_path.name}")
        
        results = {
            'class_name': class_name,
            'file_name': file_path.name,
            'start_time': time.time(),
            'test_results': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'skipped': 0
            },
            'execution_time': 0,
            'status': 'unknown'
        }
        
        try:
            # Import and instantiate the test class
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            test_class = getattr(module, class_name)
            
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            
            # Custom test result collector
            class TestResultCollector(unittest.TextTestResult):
                def __init__(self, stream, descriptions, verbosity):
                    super().__init__(stream, descriptions, verbosity)
                    self.test_details = []
                    
                def addSuccess(self, test):
                    super().addSuccess(test)
                    self.test_details.append({
                        'method': test._testMethodName,
                        'status': 'passed',
                        'message': 'Test passed successfully'
                    })
                    
                def addFailure(self, test, err):
                    super().addFailure(test, err)
                    self.test_details.append({
                        'method': test._testMethodName,
                        'status': 'failed',
                        'message': str(err[1]),
                        'traceback': ''.join(traceback.format_exception(*err))
                    })
                    
                def addError(self, test, err):
                    super().addError(test, err)
                    self.test_details.append({
                        'method': test._testMethodName,
                        'status': 'error',
                        'message': str(err[1]),
                        'traceback': ''.join(traceback.format_exception(*err))
                    })
                    
                def addSkip(self, test, reason):
                    super().addSkip(test, reason)
                    self.test_details.append({
                        'method': test._testMethodName,
                        'status': 'skipped',
                        'message': reason
                    })
            
            # Run the tests
            import io
            stream = io.StringIO()
            runner = unittest.TextTestRunner(
                stream=stream, 
                verbosity=0, 
                resultclass=TestResultCollector
            )
            
            test_result = runner.run(suite)
            
            # Collect results
            results['test_results'] = test_result.test_details
            results['summary']['total'] = test_result.testsRun
            results['summary']['failed'] = len(test_result.failures)
            results['summary']['errors'] = len(test_result.errors)
            results['summary']['skipped'] = len(test_result.skipped)
            results['summary']['passed'] = (
                results['summary']['total'] - 
                results['summary']['failed'] - 
                results['summary']['errors'] - 
                results['summary']['skipped']
            )
            
            # Determine status
            if results['summary']['errors'] > 0:
                results['status'] = 'error'
            elif results['summary']['failed'] > 0:
                results['status'] = 'failed'
            elif results['summary']['total'] == 0:
                results['status'] = 'no_tests'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'exception'
            results['error'] = str(e)
            results['traceback'] = traceback.format_exc()
            
        results['execution_time'] = time.time() - results['start_time']
        return results
        
    def run_all_discovered_tests(self):
        """Run all discovered TestKit files"""
        print("🚀 Running all discovered TestKits...")
        
        total_classes = 0
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        error_tests = 0
        
        for file_path in self.discovered_test_files:
            print(f"\n📄 Processing {file_path.name}...")
            
            # Analyze the file first
            analysis = self.analyze_test_file(file_path)
            self.test_results['discovered_tests'][str(file_path.name)] = analysis
            
            if not analysis['importable']:
                print(f"   ❌ Skipping - Import failed: {analysis.get('import_error', 'Unknown error')}")
                continue
                
            # Run each TestKit class
            file_results = []
            
            for class_info in analysis['test_classes']:
                if class_info['is_testkit']:
                    class_name = class_info['class_name']
                    total_classes += 1
                    
                    class_results = self.run_testkit_class(file_path, class_name)
                    file_results.append(class_results)
                    
                    # Update totals
                    total_tests += class_results['summary']['total']
                    passed_tests += class_results['summary']['passed']
                    failed_tests += class_results['summary']['failed']
                    error_tests += class_results['summary']['errors']
                    
                    # Print summary
                    status_icon = {
                        'passed': '✅',
                        'failed': '❌', 
                        'error': '💥',
                        'no_tests': '❓',
                        'exception': '🚨'
                    }.get(class_results['status'], '❓')
                    
                    print(f"     {status_icon} {class_name}: {class_results['summary']['passed']}/{class_results['summary']['total']} tests passed")
                    
            self.test_results['execution_results'][str(file_path.name)] = file_results
            
        # Calculate overall summary
        self.test_results['summary'] = {
            'total_files': len(self.discovered_test_files),
            'total_classes': total_classes,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'execution_time': time.time() - self.test_results.get('start_time', time.time())
        }
        
    def generate_dashboard_data(self):
        """Generate dashboard-friendly data structure"""
        summary = self.test_results['summary']
        
        # Overall health status
        success_rate = summary.get('success_rate', 0)
        if success_rate >= 90:
            health_status = 'excellent'
            health_icon = '🎉'
            health_color = 'success'
        elif success_rate >= 75:
            health_status = 'good'
            health_icon = '👍'
            health_color = 'info'
        elif success_rate >= 50:
            health_status = 'warning'
            health_icon = '⚠️'
            health_color = 'warning'
        else:
            health_status = 'critical'
            health_icon = '❌'
            health_color = 'danger'
            
        dashboard_data = {
            'overview': {
                'health_status': health_status,
                'health_icon': health_icon,
                'health_color': health_color,
                'success_rate': round(success_rate, 1),
                'total_tests': summary.get('total_tests', 0),
                'passed_tests': summary.get('passed_tests', 0),
                'failed_tests': summary.get('failed_tests', 0),
                'error_tests': summary.get('error_tests', 0)
            },
            'metrics': {
                'files_discovered': summary.get('total_files', 0),
                'testkits_executed': summary.get('total_classes', 0),
                'execution_time': round(summary.get('execution_time', 0), 2),
                'timestamp': self.test_results['timestamp']
            },
            'test_breakdown': [],
            'recent_results': []
        }
        
        # Test breakdown by file
        for file_name, file_results in self.test_results['execution_results'].items():
            for class_result in file_results:
                dashboard_data['test_breakdown'].append({
                    'file_name': file_name,
                    'class_name': class_result['class_name'],
                    'status': class_result['status'],
                    'total': class_result['summary']['total'],
                    'passed': class_result['summary']['passed'],
                    'failed': class_result['summary']['failed'],
                    'errors': class_result['summary']['errors'],
                    'execution_time': round(class_result['execution_time'], 3)
                })
                
        # Recent test results (last 5)
        dashboard_data['recent_results'] = dashboard_data['test_breakdown'][-5:]
        
        self.test_results['dashboard_data'] = dashboard_data
        
    def save_results(self):
        """Save results to JSON and generate reports"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON report
        json_path = self.reports_path / f'AutoAware_TestResults_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
            
        # Save dashboard-friendly JSON
        dashboard_path = self.reports_path / f'Dashboard_TestData_{timestamp}.json'
        with open(dashboard_path, 'w') as f:
            json.dump(self.test_results['dashboard_data'], f, indent=2, default=str)
            
        # Save latest results (for dashboard consumption)
        latest_path = self.reports_path / 'latest_test_results.json'
        with open(latest_path, 'w') as f:
            json.dump(self.test_results['dashboard_data'], f, indent=2, default=str)
            
        print(f"\n📊 Results saved:")
        print(f"   📄 Detailed: {json_path}")
        print(f"   📊 Dashboard: {dashboard_path}")
        print(f"   🔄 Latest: {latest_path}")
        
        return json_path, dashboard_path, latest_path
        
    def print_final_summary(self):
        """Print comprehensive final summary"""
        summary = self.test_results['summary']
        dashboard = self.test_results['dashboard_data']['overview']
        
        print("\n" + "=" * 80)
        print("🎯 AUTO-AWARE TESTING SYSTEM - FINAL REPORT")
        print("=" * 80)
        
        print(f"📊 Overall Health: {dashboard['health_icon']} {dashboard['health_status'].upper()}")
        print(f"✅ Success Rate: {dashboard['success_rate']}%")
        print(f"📁 Files Discovered: {summary.get('total_files', 0)}")
        print(f"🧪 TestKit Classes: {summary.get('total_classes', 0)}")
        print(f"🔍 Total Tests: {summary.get('total_tests', 0)}")
        print(f"   ✅ Passed: {summary.get('passed_tests', 0)}")
        print(f"   ❌ Failed: {summary.get('failed_tests', 0)}")
        print(f"   💥 Errors: {summary.get('error_tests', 0)}")
        print(f"⏱️ Execution Time: {summary.get('execution_time', 0):.2f}s")
        
        print("\n📋 TestKit Status Breakdown:")
        for item in self.test_results['dashboard_data']['test_breakdown']:
            status_icon = {
                'passed': '✅', 'failed': '❌', 'error': '💥', 
                'no_tests': '❓', 'exception': '🚨'
            }.get(item['status'], '❓')
            
            print(f"   {status_icon} {item['class_name']} ({item['file_name']}): "
                  f"{item['passed']}/{item['total']} tests - {item['execution_time']:.3f}s")
        
        print("=" * 80)
        
    def run_complete_system_scan(self):
        """Run the complete auto-aware testing system"""
        print("🚀 HTMX Auto-Aware Testing System")
        print("=" * 60)
        
        self.test_results['start_time'] = time.time()
        
        # Step 1: Discovery
        self.discover_all_test_files()
        
        # Step 2: Execution
        self.run_all_discovered_tests()
        
        # Step 3: Analysis
        self.generate_dashboard_data()
        
        # Step 4: Reporting
        self.save_results()
        self.print_final_summary()
        
        return self.test_results


def main():
    """Main entry point for auto-aware testing"""
    system = AutoAwareTestSystem()
    results = system.run_complete_system_scan()
    return results


if __name__ == '__main__':
    main()