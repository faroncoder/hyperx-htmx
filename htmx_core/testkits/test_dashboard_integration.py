"""
Dashboard Integration for Auto-Aware Testing System
==================================================

Provides Django views and utilities for displaying TestKit results on your dashboard.
"""

import json
from pathlib import Path
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

class TestKitDashboardMixin:
    """Mixin to provide TestKit dashboard functionality to any view"""
    
    def get_latest_test_results(self):
        """Get the latest test results for dashboard display"""
        try:
            testkits_path = Path(__file__).parent.parent
            latest_results_path = testkits_path / 'testkits' / 'reports' / 'latest_test_results.json'
            
            if latest_results_path.exists():
                with open(latest_results_path, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_dashboard_data()
                
        except Exception as e:
            return {
                'overview': {
                    'health_status': 'error',
                    'health_icon': '🚨',
                    'health_color': 'danger',
                    'success_rate': 0,
                    'error_message': str(e)
                },
                'metrics': {'error': 'Failed to load test results'},
                'test_breakdown': [],
                'recent_results': []
            }
    
    def _get_default_dashboard_data(self):
        """Return default data when no test results are available"""
        return {
            'overview': {
                'health_status': 'unknown',
                'health_icon': '❓',
                'health_color': 'secondary',
                'success_rate': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'error_tests': 0
            },
            'metrics': {
                'files_discovered': 0,
                'testkits_executed': 0,
                'execution_time': 0,
                'timestamp': 'Never'
            },
            'test_breakdown': [],
            'recent_results': []
        }
    
    def get_testkit_context(self):
        """Get TestKit data formatted for template context"""
        test_data = self.get_latest_test_results()
        
        return {
            'testkit_health': test_data['overview'],
            'testkit_metrics': test_data['metrics'],
            'testkit_tests': test_data['test_breakdown'],
            'testkit_recent': test_data['recent_results']
        }


class TestKitDashboardView(View, TestKitDashboardMixin):
    """Standalone view for TestKit dashboard"""
    
    def get(self, request):
        """Render the TestKit dashboard"""
        context = self.get_testkit_context()
        context.update({
            'page_title': 'TestKit Dashboard',
            'dashboard_type': 'testkits'
        })
        
        return render(request, 'testkits/dashboard.html', context)


class TestKitAPIView(View, TestKitDashboardMixin):
    """API view for TestKit data (JSON response)"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """Return TestKit data as JSON"""
        test_data = self.get_latest_test_results()
        
        # Add request-specific metadata
        test_data['request_info'] = {
            'timestamp': request.GET.get('timestamp'),
            'refresh_requested': request.GET.get('refresh', False),
            'format': request.GET.get('format', 'full')
        }
        
        return JsonResponse(test_data, safe=False)
    
    def post(self, request):
        """Trigger a new test run (if requested)"""
        try:
            from .test_auto_aware import AutoAwareTestSystem
            
            system = AutoAwareTestSystem()
            results = system.run_complete_system_scan()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Test run completed successfully',
                'results': results['dashboard_data']
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to run tests: {str(e)}'
            }, status=500)


# Template helper functions
def testkit_health_badge(health_status):
    """Generate HTML badge for health status"""
    status_configs = {
        'excellent': {'class': 'badge-success', 'icon': '🎉', 'text': 'Excellent'},
        'good': {'class': 'badge-info', 'icon': '👍', 'text': 'Good'},
        'warning': {'class': 'badge-warning', 'icon': '⚠️', 'text': 'Warning'},
        'critical': {'class': 'badge-danger', 'icon': '❌', 'text': 'Critical'},
        'error': {'class': 'badge-danger', 'icon': '🚨', 'text': 'Error'},
        'unknown': {'class': 'badge-secondary', 'icon': '❓', 'text': 'Unknown'}
    }
    
    config = status_configs.get(health_status, status_configs['unknown'])
    
    return f'<span class="badge {config["class"]}">{config["icon"]} {config["text"]}</span>'


def testkit_progress_bar(passed, total):
    """Generate HTML progress bar for test results"""
    if total == 0:
        return '<div class="progress"><div class="progress-bar bg-secondary" style="width: 100%">No Tests</div></div>'
    
    percentage = (passed / total) * 100
    
    if percentage >= 90:
        bar_class = 'bg-success'
    elif percentage >= 75:
        bar_class = 'bg-info'
    elif percentage >= 50:
        bar_class = 'bg-warning'
    else:
        bar_class = 'bg-danger'
    
    return f'''
    <div class="progress">
        <div class="progress-bar {bar_class}" role="progressbar" style="width: {percentage:.1f}%" 
             aria-valuenow="{passed}" aria-valuemin="0" aria-valuemax="{total}">
            {passed}/{total} ({percentage:.1f}%)
        </div>
    </div>
    '''


# URLs for Django integration (add to your urls.py)
"""
Add these URL patterns to your Django urls.py:

from htmx_core.testkits.test_dashboard_integration import TestKitDashboardView, TestKitAPIView

urlpatterns = [
    # ... your existing patterns ...
    path('dashboard/testkits/', TestKitDashboardView.as_view(), name='testkit_dashboard'),
    path('api/testkits/', TestKitAPIView.as_view(), name='testkit_api'),
]
"""

# Template example (save as templates/testkits/dashboard.html)
EXAMPLE_TEMPLATE = '''
{% load static %}

<div class="testkit-dashboard">
    <div class="row">
        <!-- Health Overview Card -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>TestKit Health {{ testkit_health.health_icon }}</h5>
                </div>
                <div class="card-body">
                    <h3 class="text-{{ testkit_health.health_color }}">
                        {{ testkit_health.success_rate }}% Success Rate
                    </h3>
                    <p>Status: <strong>{{ testkit_health.health_status|capfirst }}</strong></p>
                    
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Total Tests</small>
                            <div class="h5">{{ testkit_health.total_tests }}</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Passed</small>
                            <div class="h5 text-success">{{ testkit_health.passed_tests }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Metrics Card -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Execution Metrics</h5>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li><strong>Files:</strong> {{ testkit_metrics.files_discovered }}</li>
                        <li><strong>TestKits:</strong> {{ testkit_metrics.testkits_executed }}</li>
                        <li><strong>Runtime:</strong> {{ testkit_metrics.execution_time }}s</li>
                        <li><strong>Last Run:</strong> {{ testkit_metrics.timestamp }}</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Test Results -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Test Results</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>TestKit</th>
                                    <th>File</th>
                                    <th>Status</th>
                                    <th>Results</th>
                                    <th>Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for test in testkit_recent %}
                                <tr>
                                    <td>{{ test.class_name }}</td>
                                    <td><small class="text-muted">{{ test.file_name }}</small></td>
                                    <td>
                                        {% if test.status == 'passed' %}
                                            <span class="badge badge-success">✅ Passed</span>
                                        {% elif test.status == 'failed' %}
                                            <span class="badge badge-warning">❌ Failed</span>
                                        {% elif test.status == 'error' %}
                                            <span class="badge badge-danger">💥 Error</span>
                                        {% else %}
                                            <span class="badge badge-secondary">❓ {{ test.status }}</span>
                                        {% endif %}
                                    </td>
                                    <td>{{ test.passed }}/{{ test.total }}</td>
                                    <td><small>{{ test.execution_time }}s</small></td>
                                </tr>
                                {% empty %}
                                <tr>
                                    <td colspan="5" class="text-center text-muted">No test results available</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Auto-refresh functionality
setInterval(function() {
    fetch('/api/testkits/')
        .then(response => response.json())
        .then(data => {
            // Update dashboard elements with new data
            console.log('TestKit data updated:', data);
        })
        .catch(error => console.error('Failed to refresh TestKit data:', error));
}, 30000); // Refresh every 30 seconds
</script>
'''