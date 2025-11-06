"""
Dashboard Views for HTMX Core TestKit Integration
===============================================

Add these views to your main Django application to display TestKit results on your dashboard.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from htmx_core.testkits.test_dashboard_integration import TestKitDashboardMixin
import json
import subprocess
from pathlib import Path


class MainDashboardView(View, TestKitDashboardMixin):
    """Main dashboard view with TestKit integration"""
    
    def get(self, request):
        """Render main dashboard with TestKit status"""
        # Get TestKit data
        testkit_data = self.get_testkit_context()
        
        # Your existing dashboard context
        context = {
            'page_title': 'S5Portal Dashboard',
            'user': request.user,
            # Add TestKit data
            **testkit_data,
            # Your other dashboard data...
        }
        
        return render(request, 'dashboard/main_dashboard.html', context)


class TestKitStatusAPIView(View, TestKitDashboardMixin):
    """API endpoint for TestKit status (for HTMX updates)"""
    
    def get(self, request):
        """Return current TestKit status"""
        data = self.get_latest_test_results()
        
        # Format for HTMX response
        formatted_data = {
            'status': data['overview']['health_status'],
            'icon': data['overview']['health_icon'],
            'success_rate': data['overview']['success_rate'],
            'total_tests': data['overview']['total_tests'],
            'passed_tests': data['overview']['passed_tests'],
            'failed_tests': data['overview']['failed_tests'],
            'error_tests': data['overview']['error_tests'],
            'last_run': data['metrics']['timestamp'],
            'execution_time': data['metrics']['execution_time']
        }
        
        return JsonResponse(formatted_data)


class RunTestKitAPIView(View):
    """API endpoint to trigger TestKit execution"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Run TestKit system and return results"""
        try:
            # Path to the auto-aware test script
            script_path = Path(__file__).parent / 'testkits' / 'test_auto_aware.py'
            
            # Run the test system
            result = subprocess.run(
                ['python', str(script_path)], 
                capture_output=True, 
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if result.returncode == 0:
                return JsonResponse({
                    'status': 'success',
                    'message': 'TestKit execution completed successfully',
                    'output': result.stdout
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'TestKit execution failed',
                    'error': result.stderr
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to run TestKit system: {str(e)}'
            }, status=500)


# Template fragments for HTMX integration
TESTKIT_STATUS_TEMPLATE = '''
<!-- TestKit Status Card (add to your main dashboard) -->
<div class="card testkit-status-card" id="testkit-status">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
            <i class="fas fa-vial me-2"></i>TestKit Status
        </h5>
        <button class="btn btn-sm btn-outline-primary" 
                hx-post="/api/testkits/run/" 
                hx-target="#testkit-status"
                hx-indicator="#testkit-loading">
            <i class="fas fa-play me-1"></i>Run Tests
        </button>
    </div>
    <div class="card-body">
        <!-- Loading indicator -->
        <div id="testkit-loading" class="htmx-indicator">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>Running tests...</span>
            </div>
        </div>
        
        <!-- TestKit status content -->
        <div hx-get="/api/testkits/status/" 
             hx-trigger="load, every 60s" 
             hx-target="#testkit-content">
            <div id="testkit-content">
                {% if testkit_health %}
                <div class="row g-3">
                    <div class="col-md-8">
                        <div class="d-flex align-items-center mb-2">
                            <span class="fs-2 me-2">{{ testkit_health.health_icon }}</span>
                            <div>
                                <h6 class="mb-0 text-{{ testkit_health.health_color }}">
                                    {{ testkit_health.health_status|capfirst }}
                                </h6>
                                <small class="text-muted">{{ testkit_health.success_rate }}% Success Rate</small>
                            </div>
                        </div>
                        
                        <div class="progress mb-2" style="height: 8px;">
                            <div class="progress-bar bg-{{ testkit_health.health_color }}" 
                                 style="width: {{ testkit_health.success_rate }}%"></div>
                        </div>
                        
                        <div class="row text-center">
                            <div class="col-3">
                                <div class="text-success fw-bold">{{ testkit_health.passed_tests }}</div>
                                <small class="text-muted">Passed</small>
                            </div>
                            <div class="col-3">
                                <div class="text-warning fw-bold">{{ testkit_health.failed_tests }}</div>
                                <small class="text-muted">Failed</small>
                            </div>
                            <div class="col-3">
                                <div class="text-danger fw-bold">{{ testkit_health.error_tests }}</div>
                                <small class="text-muted">Errors</small>
                            </div>
                            <div class="col-3">
                                <div class="fw-bold">{{ testkit_health.total_tests }}</div>
                                <small class="text-muted">Total</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <ul class="list-unstyled mb-0">
                            <li><small><strong>Files:</strong> {{ testkit_metrics.files_discovered }}</small></li>
                            <li><small><strong>TestKits:</strong> {{ testkit_metrics.testkits_executed }}</small></li>
                            <li><small><strong>Runtime:</strong> {{ testkit_metrics.execution_time }}s</small></li>
                            <li><small><strong>Last Run:</strong> 
                                <span title="{{ testkit_metrics.timestamp }}">
                                    {{ testkit_metrics.timestamp|timesince }} ago
                                </span>
                            </small></li>
                        </ul>
                    </div>
                </div>
                {% else %}
                <div class="text-center text-muted">
                    <i class="fas fa-question-circle fs-1 mb-2"></i>
                    <p>No TestKit results available</p>
                    <small>Click "Run Tests" to execute the TestKit system</small>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Recent TestKit Results -->
<div class="card mt-3" id="testkit-recent">
    <div class="card-header">
        <h6 class="mb-0">Recent TestKit Results</h6>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-sm mb-0">
                <thead class="table-light">
                    <tr>
                        <th>TestKit</th>
                        <th>Status</th>
                        <th>Results</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test in testkit_recent %}
                    <tr>
                        <td>
                            <small class="fw-bold">{{ test.class_name }}</small><br>
                            <small class="text-muted">{{ test.file_name }}</small>
                        </td>
                        <td>
                            {% if test.status == 'passed' %}
                                <span class="badge bg-success">✅ Passed</span>
                            {% elif test.status == 'failed' %}
                                <span class="badge bg-warning">❌ Failed</span>
                            {% elif test.status == 'error' %}
                                <span class="badge bg-danger">💥 Error</span>
                            {% else %}
                                <span class="badge bg-secondary">❓ {{ test.status }}</span>
                            {% endif %}
                        </td>
                        <td>
                            <small>{{ test.passed }}/{{ test.total }}</small>
                            <div class="progress" style="height: 4px; width: 60px;">
                                {% widthratio test.passed test.total 100 as percentage %}
                                <div class="progress-bar 
                                    {% if percentage >= 90 %}bg-success
                                    {% elif percentage >= 75 %}bg-info
                                    {% elif percentage >= 50 %}bg-warning
                                    {% else %}bg-danger{% endif %}" 
                                     style="width: {{ percentage }}%"></div>
                            </div>
                        </td>
                        <td><small>{{ test.execution_time }}s</small></td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="4" class="text-center text-muted py-3">
                            No recent test results
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
'''

# Add to your URLs
"""
Add these to your main urls.py:

from htmx_core.testkits.dashboard_views import MainDashboardView, TestKitStatusAPIView, RunTestKitAPIView

urlpatterns = [
    # Your existing patterns...
    path('', MainDashboardView.as_view(), name='main_dashboard'),
    path('api/testkits/status/', TestKitStatusAPIView.as_view(), name='testkit_status_api'),
    path('api/testkits/run/', RunTestKitAPIView.as_view(), name='run_testkit_api'),
]
"""