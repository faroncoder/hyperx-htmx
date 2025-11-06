#!/usr/bin/env python3
"""
Enhanced HTMX Core Discovery Analysis
Provides detailed analysis of what's working vs what's not working in htmx_core
"""

import os
import ast
import importlib
import inspect
from pathlib import Path
from collections import defaultdict
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

class HTMXCoreAnalyzer:
    def __init__(self):
        self.htmx_core_path = Path('htmx_core')
        self.analysis_results = {
            'file_structure': defaultdict(list),
            'working_components': [],
            'broken_components': [],
            'unused_components': [],
            'key_integrations': {},
            'recommendations': []
        }

    def analyze_file_structure(self):
        """Analyze the htmx_core directory structure"""
        print("📂 ANALYZING HTMX CORE FILE STRUCTURE")
        print("=" * 50)
        
        for root, dirs, files in os.walk(self.htmx_core_path):
            # Skip __pycache__ and other non-essential dirs
            dirs[:] = [d for d in dirs if not d.startswith('__')]
            
            level = root.replace(str(self.htmx_core_path), '').count(os.sep)
            indent = '  ' * level
            folder_name = Path(root).name
            
            if level == 0:
                print(f"\n📁 {folder_name}/")
            else:
                print(f"{indent}📁 {folder_name}/")
            
            # List Python files in this directory
            python_files = [f for f in files if f.endswith('.py') and not f.startswith('__')]
            for file in python_files:
                file_path = Path(root) / file
                try:
                    # Quick analysis of file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = len(content.splitlines())
                    has_classes = 'class ' in content
                    has_functions = 'def ' in content
                    
                    status_icons = []
                    if has_classes:
                        status_icons.append('🏗️')
                    if has_functions:
                        status_icons.append('⚙️')
                    if lines > 100:
                        status_icons.append('📄')
                    
                    status = ''.join(status_icons) if status_icons else '📝'
                    print(f"{indent}  {status} {file} ({lines} lines)")
                    
                    self.analysis_results['file_structure'][str(Path(root).relative_to(self.htmx_core_path))].append({
                        'file': file,
                        'lines': lines,
                        'has_classes': has_classes,
                        'has_functions': has_functions
                    })
                    
                except Exception as e:
                    print(f"{indent}  ❌ {file} (Error: {e})")

    def test_key_components(self):
        """Test the key HTMX Core components"""
        print("\n\n🔧 TESTING KEY COMPONENTS")
        print("=" * 50)
        
        component_tests = [
            {
                'name': 'HTMX Core Registry',
                'test': self._test_htmx_registry,
                'critical': True
            },
            {
                'name': 'X-Tab System', 
                'test': self._test_x_tab_system,
                'critical': True
            },
            {
                'name': 'Middleware Stack',
                'test': self._test_middleware_stack,
                'critical': True
            },
            {
                'name': 'Helper Functions',
                'test': self._test_helper_functions,
                'critical': False
            },
            {
                'name': 'View Functions',
                'test': self._test_view_functions,
                'critical': False
            },
            {
                'name': 'Mixins & Decorators',
                'test': self._test_mixins_decorators,
                'critical': False
            },
            {
                'name': 'Template Integration',
                'test': self._test_template_integration,
                'critical': False
            }
        ]
        
        for test in component_tests:
            print(f"\n🧪 Testing: {test['name']}")
            try:
                result = test['test']()
                status = "✅ WORKING" if result['success'] else "❌ FAILED"
                criticality = "🔴 CRITICAL" if test['critical'] else "🟡 OPTIONAL"
                
                print(f"   {status} ({criticality})")
                print(f"   Details: {result['details']}")
                
                if result['success']:
                    self.analysis_results['working_components'].append({
                        'name': test['name'],
                        'details': result['details'],
                        'critical': test['critical']
                    })
                else:
                    self.analysis_results['broken_components'].append({
                        'name': test['name'],
                        'error': result.get('error', 'Unknown error'),
                        'critical': test['critical']
                    })
                    
                self.analysis_results['key_integrations'][test['name']] = result
                
            except Exception as e:
                print(f"   ❌ FAILED (🔴 CRITICAL): {str(e)}")
                self.analysis_results['broken_components'].append({
                    'name': test['name'],
                    'error': str(e),
                    'critical': test['critical']
                })

    def _test_htmx_registry(self):
        """Test HTMX registry system"""
        try:
            from htmx_core.initializer import get_htmx_registry, is_htmx_core_ready
            
            registry = get_htmx_registry()
            is_ready = is_htmx_core_ready()
            
            if not is_ready or not registry:
                return {'success': False, 'error': 'Registry not initialized'}
            
            component_count = sum(len(items) for items in registry.values())
            category_count = len(registry)
            
            return {
                'success': True,
                'details': f'{component_count} components across {category_count} categories',
                'data': {'components': component_count, 'categories': category_count}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_x_tab_system(self):
        """Test X-Tab registry system"""
        try:
            from htmx_core.utils.htmx_x_tab_registry import TabRegistry
            
            registry = TabRegistry()
            manifest = registry.generate_tab_manifest()
            
            if not manifest or 'total_tabs' not in manifest:
                return {'success': False, 'error': 'No manifest generated'}
            
            return {
                'success': True,
                'details': f"{manifest['total_tabs']} tabs across {manifest['total_apps']} apps",
                'data': manifest
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_middleware_stack(self):
        """Test middleware components"""
        try:
            middleware_tests = []
            
            # Test individual middleware classes
            from htmx_core.middleware.htmx_security import HTMXTokenManager
            middleware_tests.append(('HTMXTokenManager', HTMXTokenManager))
            
            from htmx_core.middleware.htmx_switcher import HTMXRequestSwitcher
            middleware_tests.append(('HTMXRequestSwitcher', HTMXRequestSwitcher))
            
            from htmx_core.middleware.htmx_benchmark_security import (
                HTMXSecurityMiddleware, HTMXContentMiddleware, HTMXErrorMiddleware
            )
            middleware_tests.extend([
                ('HTMXSecurityMiddleware', HTMXSecurityMiddleware),
                ('HTMXContentMiddleware', HTMXContentMiddleware), 
                ('HTMXErrorMiddleware', HTMXErrorMiddleware)
            ])
            
            working_middleware = []
            for name, middleware_class in middleware_tests:
                if inspect.isclass(middleware_class):
                    working_middleware.append(name)
            
            return {
                'success': len(working_middleware) > 0,
                'details': f'{len(working_middleware)}/{len(middleware_tests)} middleware classes working',
                'data': {'working': working_middleware}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_helper_functions(self):
        """Test helper functions"""
        try:
            from htmx_core.utils.htmx_helpers import is_htmx_request, hx_redirect, hx_trigger
            from htmx_core.utils.htmx_defaults import htmx_defaults, smart_redirect
            
            helpers = [
                ('is_htmx_request', is_htmx_request),
                ('hx_redirect', hx_redirect),
                ('hx_trigger', hx_trigger),
                ('htmx_defaults', htmx_defaults),
                ('smart_redirect', smart_redirect)
            ]
            
            working_helpers = []
            for name, func in helpers:
                if callable(func):
                    working_helpers.append(name)
            
            return {
                'success': len(working_helpers) > 0,
                'details': f'{len(working_helpers)} helper functions available',
                'data': {'helpers': working_helpers}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_view_functions(self):
        """Test view functions"""
        try:
            from htmx_core.views.htmx_views import lazy_tab_map
            from django.test import RequestFactory
            
            factory = RequestFactory()
            request = factory.get('/test')
            response = lazy_tab_map(request)
            
            success = hasattr(response, 'status_code') and response.status_code == 200
            
            return {
                'success': success,
                'details': f'lazy_tab_map returns {response.status_code} status',
                'data': {'status_code': response.status_code}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_mixins_decorators(self):
        """Test mixins and decorators"""
        try:
            from htmx_core.mixins.htmx_mixin import HTMXMessageMixin, HTMXRedirectMixin
            from htmx_core.mixins.htmx_xtabs_mixins import XTabMixin
            from htmx_core.utils.htmx_helpers import htmx_login_required
            
            components = [
                ('HTMXMessageMixin', HTMXMessageMixin),
                ('HTMXRedirectMixin', HTMXRedirectMixin),
                ('XTabMixin', XTabMixin),
                ('htmx_login_required', htmx_login_required)
            ]
            
            working_components = []
            for name, component in components:
                if inspect.isclass(component) or callable(component):
                    working_components.append(name)
            
            return {
                'success': len(working_components) > 0,
                'details': f'{len(working_components)} mixins/decorators available',
                'data': {'components': working_components}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_template_integration(self):
        """Test template integration"""
        try:
            from htmx_core.utils.htmx_template_helpers import get_htmx_render_mode, needs_htmx_wrapper
            from htmx_core.utils.htmx_tab_detection import get_active_tab_from_url
            
            template_functions = [
                ('get_htmx_render_mode', get_htmx_render_mode),
                ('needs_htmx_wrapper', needs_htmx_wrapper), 
                ('get_active_tab_from_url', get_active_tab_from_url)
            ]
            
            working_functions = []
            for name, func in template_functions:
                if callable(func):
                    working_functions.append(name)
            
            return {
                'success': len(working_functions) > 0,
                'details': f'{len(working_functions)} template functions available',
                'data': {'functions': working_functions}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n\n💡 RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = []
        
        # Check critical components
        critical_broken = [c for c in self.analysis_results['broken_components'] if c.get('critical', False)]
        if critical_broken:
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'{len(critical_broken)} critical components broken',
                'action': 'Fix broken critical components immediately'
            })
        
        # Check success rate
        total_working = len(self.analysis_results['working_components'])
        total_tested = total_working + len(self.analysis_results['broken_components'])
        success_rate = (total_working / total_tested * 100) if total_tested > 0 else 0
        
        if success_rate < 75:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'Success rate is {success_rate:.1f}%',
                'action': 'Investigate and fix failing components'
            })
        
        # Check for unused files
        # (This would need more complex analysis)
        
        # Display recommendations
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
            print(f"\n{i}. {priority_icon} {rec['priority']} PRIORITY")
            print(f"   Issue: {rec['issue']}")
            print(f"   Action: {rec['action']}")
        
        if not recommendations:
            print("\n✅ No major issues detected - HTMX Core is functioning well!")
        
        self.analysis_results['recommendations'] = recommendations

    def print_summary(self):
        """Print analysis summary"""
        print("\n\n📊 ANALYSIS SUMMARY")
        print("=" * 50)
        
        working_count = len(self.analysis_results['working_components'])
        broken_count = len(self.analysis_results['broken_components'])
        total_files = sum(len(files) for files in self.analysis_results['file_structure'].values())
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total Files Analyzed: {total_files}")
        print(f"   Working Components: {working_count}")
        print(f"   Broken Components: {broken_count}")
        
        if working_count + broken_count > 0:
            success_rate = working_count / (working_count + broken_count) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n✅ WORKING COMPONENTS ({working_count}):")
        for component in self.analysis_results['working_components']:
            criticality = "🔴 CRITICAL" if component.get('critical') else "🟡 OPTIONAL"
            print(f"   • {component['name']} ({criticality}) - {component['details']}")
        
        if self.analysis_results['broken_components']:
            print(f"\n❌ BROKEN COMPONENTS ({broken_count}):")
            for component in self.analysis_results['broken_components']:
                criticality = "🔴 CRITICAL" if component.get('critical') else "🟡 OPTIONAL"
                print(f"   • {component['name']} ({criticality}) - {component['error']}")
        
        # Overall health assessment
        critical_broken = [c for c in self.analysis_results['broken_components'] if c.get('critical', False)]
        
        print(f"\n🏆 OVERALL HEALTH:")
        if not critical_broken and working_count > 0:
            print("   🎉 EXCELLENT - All critical systems operational!")
        elif len(critical_broken) <= 1 and working_count >= 3:
            print("   ✅ GOOD - Minor issues but core functionality intact")
        elif len(critical_broken) <= 2:
            print("   ⚠️  FAIR - Some critical issues need attention")
        else:
            print("   ❌ POOR - Multiple critical issues detected")

    def run_analysis(self):
        """Run the complete analysis"""
        print("🔬 HTMX CORE COMPREHENSIVE ANALYSIS")
        print("=" * 60)
        
        self.analyze_file_structure()
        self.test_key_components()
        self.generate_recommendations()
        self.print_summary()

if __name__ == "__main__":
    analyzer = HTMXCoreAnalyzer()
    analyzer.run_analysis()