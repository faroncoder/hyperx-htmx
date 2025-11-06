"""
System Health TestKit
===================

Overall system health and integration testing.
"""

import os
import sys
import importlib
import django
from pathlib import Path
from typing import Dict, List, Any

# Handle imports for both direct execution and module import
try:
    from .test_base_testkit import BaseTestKit
except ImportError:
    # Direct execution - use absolute import
    from test_base_testkit import BaseTestKit

class SystemHealthKit(BaseTestKit):
    """TestKit for overall system health validation"""
    
    def setUp(self):
        super().setUp()
        self.health_metrics = {}
    
    def test_django_setup(self):
        """Test Django environment setup"""
        print("🔧 Testing Django setup...")
        
        try:
            # Check Django configuration
            django_setup_success = True
            django_version = django.VERSION
            
            # Test settings import
            from django.conf import settings
            debug_mode = getattr(settings, 'DEBUG', False)
            installed_apps = getattr(settings, 'INSTALLED_APPS', [])
            
            self.health_metrics['django'] = {
                'version': django_version,
                'debug_mode': debug_mode,
                'installed_apps_count': len(installed_apps),
                'htmx_core_installed': any('htmx_core' in app for app in installed_apps)
            }
            
            message = f"Django {'.'.join(map(str, django_version[:2]))} configured with {len(installed_apps)} apps"
            
            self.add_test_result("Django Setup", django_setup_success, message, self.health_metrics['django'])
            
            print(f"   ✅ Django: v{'.'.join(map(str, django_version[:2]))}, {len(installed_apps)} apps")
            
        except Exception as e:
            self.add_test_result("Django Setup", False, f"Django setup failed: {str(e)}")
            print(f"   ❌ Django setup: {e}")
    
    def test_project_structure(self):
        """Test basic project structure"""
        print("📁 Testing project structure...")
        
        required_paths = [
            'manage.py',
            'config/',
            'htmx_core/',
            'templates/',
            'static/',
        ]
        
        structure_results = []
        missing_paths = []
        
        for path in required_paths:
            full_path = self.project_root / path
            exists = full_path.exists()
            
            structure_results.append({
                'path': path,
                'exists': exists,
                'type': 'directory' if path.endswith('/') else 'file'
            })
            
            if not exists:
                missing_paths.append(path)
        
        success = len(missing_paths) == 0
        message = f"Project structure: {len(required_paths) - len(missing_paths)}/{len(required_paths)} required paths found"
        
        self.add_test_result("Project Structure", success, message, {
            'required_paths': len(required_paths),
            'found_paths': len(required_paths) - len(missing_paths),
            'missing_paths': missing_paths,
            'structure_results': structure_results
        })
        
        print(f"   📁 Structure: {len(required_paths) - len(missing_paths)}/{len(required_paths)} paths found")
    
    def test_python_environment(self):
        """Test Python environment"""
        print("🐍 Testing Python environment...")
        
        try:
            python_version = sys.version_info
            python_executable = sys.executable
            
            # Check important modules
            important_modules = ['django', 'pathlib', 'ast', 'unittest', 'importlib']
            available_modules = []
            
            for module_name in important_modules:
                try:
                    importlib.import_module(module_name)
                    available_modules.append(module_name)
                except ImportError:
                    pass
            
            env_info = {
                'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                'python_executable': python_executable,
                'available_modules': available_modules,
                'module_availability': len(available_modules) / len(important_modules) * 100
            }
            
            success = len(available_modules) == len(important_modules)
            message = f"Python {env_info['python_version']}: {len(available_modules)}/{len(important_modules)} modules available"
            
            self.add_test_result("Python Environment", success, message, env_info)
            
            print(f"   🐍 Python: v{env_info['python_version']}, {len(available_modules)}/{len(important_modules)} modules")
            
        except Exception as e:
            self.add_test_result("Python Environment", False, f"Python environment test failed: {str(e)}")
            print(f"   ❌ Python environment: {e}")
    
    def test_file_permissions(self):
        """Test file system permissions"""
        print("🔐 Testing file permissions...")
        
        test_paths = [
            self.project_root / 'testkits' / 'reports',
            self.project_root / 'logs',
            self.project_root / 'media',
        ]
        
        permission_results = []
        
        for path in test_paths:
            try:
                # Ensure path exists
                path.mkdir(parents=True, exist_ok=True)
                
                # Test read permission
                can_read = os.access(path, os.R_OK)
                
                # Test write permission
                can_write = os.access(path, os.W_OK)
                
                # Test execute permission (for directories)
                can_execute = os.access(path, os.X_OK)
                
                permission_results.append({
                    'path': str(path),
                    'readable': can_read,
                    'writable': can_write,
                    'executable': can_execute,
                    'all_permissions': can_read and can_write and can_execute
                })
                
            except Exception as e:
                permission_results.append({
                    'path': str(path),
                    'error': str(e),
                    'all_permissions': False
                })
        
        successful_permissions = sum(1 for result in permission_results if result.get('all_permissions', False))
        
        success = successful_permissions == len(permission_results)
        message = f"File permissions: {successful_permissions}/{len(permission_results)} paths accessible"
        
        self.add_test_result("File Permissions", success, message, {
            'tested_paths': len(permission_results),
            'accessible_paths': successful_permissions,
            'permission_results': permission_results
        })
        
        print(f"   🔐 Permissions: {successful_permissions}/{len(permission_results)} paths accessible")
    
    def test_testkit_framework(self):
        """Test TestKit framework components"""
        print("🧪 Testing TestKit framework...")
        
        try:
            # Test imports with fallback
            try:
                from .test_base_testkit import BaseTestKit
                from .test_reporter import TestKitReporter
            except ImportError:
                from test_base_testkit import BaseTestKit
                from test_reporter import TestKitReporter
            
            framework_components = []
            
            # Test BaseTestKit
            try:
                base_kit = BaseTestKit()
                framework_components.append({
                    'component': 'BaseTestKit',
                    'success': True,
                    'message': 'BaseTestKit instantiated successfully'
                })
            except Exception as e:
                framework_components.append({
                    'component': 'BaseTestKit', 
                    'success': False,
                    'message': str(e)
                })
            
            # Test Reporter
            try:
                reporter = TestKitReporter()
                framework_components.append({
                    'component': 'TestKitReporter',
                    'success': True,
                    'message': 'TestKitReporter instantiated successfully'
                })
            except Exception as e:
                framework_components.append({
                    'component': 'TestKitReporter',
                    'success': False,
                    'message': str(e)
                })
            
            successful_components = sum(1 for comp in framework_components if comp['success'])
            success = successful_components == len(framework_components)
            message = f"TestKit framework: {successful_components}/{len(framework_components)} components working"
            
            self.add_test_result("TestKit Framework", success, message, {
                'framework_components': framework_components,
                'success_rate': successful_components / len(framework_components) * 100 if framework_components else 0
            })
            
            print(f"   🧪 Framework: {successful_components}/{len(framework_components)} components working")
            
        except Exception as e:
            self.add_test_result("TestKit Framework", False, f"Framework test failed: {str(e)}")
            print(f"   ❌ Framework: {e}")
    
    def tearDown(self):
        """Generate system health summary"""
        # Calculate overall health metrics
        total_tests = len(self.test_results['tests'])
        passed_tests = sum(1 for test in self.test_results['tests'] if test.get('success', False))
        
        if total_tests > 0:
            health_score = (passed_tests / total_tests) * 100
        else:
            health_score = 0
        
        # Determine system status
        if health_score >= 95:
            system_status = "Excellent"
        elif health_score >= 85:
            system_status = "Good"
        elif health_score >= 70:
            system_status = "Fair"
        else:
            system_status = "Needs Attention"
        
        self.test_results['summary'] = {
            'Total Health Tests': total_tests,
            'Passed Tests': passed_tests,
            'Health Score': f"{health_score:.1f}%",
            'System Status': system_status,
            'Django Configured': bool(self.health_metrics.get('django', {}).get('version')),
            'HTMX Core Available': bool(self.health_metrics.get('django', {}).get('htmx_core_installed')),
        }
        
        print("\n" + "="*60)
        print("🏥 SYSTEM HEALTH SUMMARY")
        print("="*60)
        for key, value in self.test_results['summary'].items():
            print(f"{key}: {value}")
        print("="*60)
        
        super().tearDown()

if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)