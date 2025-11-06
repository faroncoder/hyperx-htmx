from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.conf import settings
import json
import time
from datetime import datetime, timedelta
from htmx_core.views import *
from htmx_core.utils import *
from htmx_core.mixins import *
from htmx_core.dispatchers import *
from .models import *

# views.py
import os
from django.http import JsonResponse
from django.conf import settings




def showcase_home(request):
    """Main showcase page demonstrating HyperX declarative components"""
    tasks = Task.objects.all()[:5] if request.user.is_authenticated else []
    
    context = {
        'tasks': tasks,
        'total_tasks': Task.objects.count() if request.user.is_authenticated else 0,
        'completed_tasks': Task.objects.filter(completed=True).count() if request.user.is_authenticated else 0,
    }
    
    response = render(request, 'declaratives/showcase_home.html', context)
    
    # Add default HTMX target to body
    if request.htmx:
        response['HX-Retarget'] = 'body'
    
    return response


def component_gallery(request):
    """Component Gallery - comprehensive testing interface for all HyperX patterns"""
    return render(request, 'declaratives/component_gallery.html', {
        'page_title': 'HyperX Component Gallery'
    })


def hyperx_playground(request):
    """HyperX Playground - Interactive testing environment for URL patterns"""
    from django.urls import reverse
    
    # Generate a dynamic list of available endpoints for testing
    available_endpoints = {
        'Component APIs': [
            ('Table Data', reverse('declaratives:paginated_table_data')),
            ('Live Charts', reverse('declaratives:live_stats')),
            ('Real-time Activity', reverse('declaratives:live_activity')),
            ('Toast Notifications', reverse('declaratives:show_toast')),
        ],
        'Advanced Patterns': [
            ('Dynamic Component', reverse('declaratives:dynamic_form_handler')),
            ('REST API Tasks', reverse('declaratives:task_form_handler')),
            ('SSE Stream', reverse('declaratives:sse_stream', args=['notifications'])),
            ('Test Polling', reverse('declaratives:test_polling', args=[2])),
        ],
        'Debug Tools': [
            ('Component Health', reverse('declaratives:component_health')),
            ('HTMX Debug', reverse('declaratives:htmx_debug')),
            ('Performance Debug', reverse('declaratives:performance_debug')),
        ] if settings.DEBUG else []
    }
    
    context = {
        'page_title': 'HyperX Playground',
        'endpoints': available_endpoints,
        'current_url_pattern': request.resolver_match.url_name if request.resolver_match else None
    }
    
    return render(request, 'declaratives/hyperx_playground.html', context)


def live_search_tasks(request):
    """Demonstrate htmx_live_search functionality"""
    query = request.GET.get('q', '')
    
    if query:
        tasks = Task.objects.filter(
            title__icontains=query
        ).select_related('created_by')[:10]
    else:
        tasks = Task.objects.all()[:5]
    
    # Simulate search delay for demonstration
    time.sleep(0.2)
    
    context = {'tasks': tasks, 'query': query}
    
    if request.htmx:
        return render(request, 'declaratives/partials/task_search_results.html', context)
    
    return render(request, 'declaratives/search_page.html', context)


@require_http_methods(["POST"])
def quick_add_task(request):
    """Demonstrate htmx_form_submit with instant feedback"""
    title = request.POST.get('title', '').strip()
    
    if not title:
        return HttpResponse('<div class="alert alert-danger">Task title is required</div>')
    
    if not request.user.is_authenticated:
        return HttpResponse('<div class="alert alert-warning">Please log in to add tasks</div>')
    
    task = Task.objects.create(
        title=title,
        created_by=request.user
    )
    
    if request.htmx:
        # Return the new task row and clear the form
        context = {'task': task}
        task_html = render_to_string('declaratives/partials/task_row.html', context, request)
        
        return HttpResponse(f'''
            <div id="task-{task.id}" class="task-row fade-in">{task_html}</div>
            <script>
                document.getElementById('quick-add-form').reset();
                document.getElementById('task-count').innerText = '{Task.objects.count()}';
            </script>
        ''')
    
    messages.success(request, f'Task "{title}" created successfully!')
    return redirect('declaratives:showcase_home')


@require_http_methods(["POST"])
def toggle_task(request, task_id):
    """Demonstrate htmx_trigger for instant state updates"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.user.is_authenticated and task.created_by == request.user:
        task.completed = not task.completed
        task.save()
    
    if request.htmx:
        context = {'task': task}
        return render(request, 'declaratives/partials/task_row.html', context)
    
    return redirect('declaratives:showcase_home')


@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    """Demonstrate htmx_delete_confirm functionality"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.user.is_authenticated and task.created_by == request.user:
        task.delete()
        
        if request.htmx:
            return HttpResponse(f'''
                <div class="alert alert-success fade-in">
                    Task deleted successfully!
                </div>
                <script>
                    document.getElementById('task-count').innerText = '{Task.objects.count()}';
                </script>
            ''')
    
    return HttpResponse('<div class="alert alert-danger">Permission denied</div>')


def live_metrics_api(request):
    """API endpoint for htmx_polling demonstration - Updates individual metric elements"""
    # Generate some live metrics
    metrics = {
        'total_tasks': Task.objects.count(),
        'completed_tasks': Task.objects.filter(completed=True).count(),
        'pending_tasks': Task.objects.filter(completed=False).count(),
        'users_online': 1 if request.user.is_authenticated else 0,
        'last_update': datetime.now().strftime('%H:%M:%S'),
    }
    
    if request.htmx:
        # Return multiple out-of-band updates targeting specific elements
        return HttpResponse(f'''
            <h3 id="total-tasks-count" hx-swap-oob="true">{metrics['total_tasks']}</h3>
            <h3 id="completed-tasks-count" hx-swap-oob="true">{metrics['completed_tasks']}</h3>
            <h3 id="users-online-count" hx-swap-oob="true">{metrics['users_online']}</h3>
            <h3 id="last-update-time" hx-swap-oob="true">{metrics['last_update']}</h3>
        ''')
    
    return JsonResponse(metrics)


def lazy_load_comments(request, task_id):
    """Demonstrate htmx_lazy_load for performance optimization"""
    task = get_object_or_404(Task, id=task_id)
    
    # Simulate slow loading
    time.sleep(0.5)
    
    comments = Comment.objects.filter(task=task).select_related('author')
    
    context = {'task': task, 'comments': comments}
    return render(request, 'declaratives/partials/comments_section.html', context)


@require_http_methods(["POST"])
def add_comment(request, task_id):
    """Demonstrate real-time comment addition"""
    task = get_object_or_404(Task, id=task_id)
    content = request.POST.get('content', '').strip()
    
    if not content or not request.user.is_authenticated:
        return HttpResponse('<div class="alert alert-warning">Please log in and provide content</div>')
    
    comment = Comment.objects.create(
        task=task,
        author=request.user,
        content=content
    )
    
    if request.htmx:
        context = {'comment': comment}
        comment_html = render_to_string('declaratives/partials/comment_item.html', context, request)
        
        return HttpResponse(f'''
            <div class="comment-item fade-in">{comment_html}</div>
            <script>
                document.getElementById('comment-form-{task_id}').reset();
            </script>
        ''')
    
    return redirect('declaratives:showcase_home')


def websocket_demo(request):
    """Demonstrate htmx_websocket connectivity"""
    return render(request, 'declaratives/websocket_demo.html')


def form_validation_demo(request):
    """Demonstrate htmx_validate_field patterns"""
    return render(request, 'declaratives/form_validation_demo.html')


@require_http_methods(["POST"])
def validate_task_title(request):
    """Real-time validation endpoint"""
    title = request.POST.get('title', '').strip()
    
    if len(title) < 3:
        return HttpResponse(
            '<div class="text-danger small">Title must be at least 3 characters</div>'
        )
    
    if Task.objects.filter(title__iexact=title, created_by=request.user).exists():
        return HttpResponse(
            '<div class="text-warning small">You already have a task with this title</div>'
        )
    
    return HttpResponse(
        '<div class="text-success small">✓ Title looks good!</div>'
    )


def reset_demo_data(request):
    """Reset demo data for development"""
    if request.method == 'POST':
        # Clear existing demo data
        Task.objects.filter(title__startswith='Demo').delete()
        Comment.objects.filter(content__startswith='Demo').delete()
        
        # Create fresh demo data
        demo_tasks = [
            {'title': 'Demo Task 1', 'description': 'First demo task'},
            {'title': 'Demo Task 2', 'description': 'Second demo task'},
            {'title': 'Demo Task 3', 'description': 'Third demo task'},
        ]
        
        for task_data in demo_tasks:
            Task.objects.create(**task_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Demo data reset successfully',
            'created_tasks': len(demo_tasks)
        })
    
    return JsonResponse({'error': 'POST method required'})


def generate_demo_data(request):
    """Generate demo data for development"""
    if request.method == 'POST':
        import random
        
        # Generate random demo tasks
        for i in range(10):
            Task.objects.create(
                title=f'Generated Task {i+1}',
                description=f'Auto-generated demo task number {i+1}',
                completed=random.choice([True, False])
            )
        
        # Generate demo comments
        tasks = Task.objects.all()[:5]
        for task in tasks:
            Comment.objects.create(
                task=task,
                content=f'Demo comment for {task.title}',
                author='demo_user'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Demo data generated successfully',
            'created_tasks': 10,
            'created_comments': len(tasks)
        })
    
    return JsonResponse({'error': 'POST method required'})


# ===============================================
# NEW DYNAMIC COMPONENT API ENDPOINTS
# ===============================================

def api_system_performance(request):
    """API endpoint for real-time system performance metrics"""
    import random
    from django.utils import timezone
    
    if request.method == 'GET':
        # Get latest performance data or generate real-time simulation
        latest_metrics = SystemPerformance.objects.first()
        
        if latest_metrics:
            # Return actual database data with slight real-time variation
            data = {
                'cpu': min(100, max(0, latest_metrics.cpu_usage + random.uniform(-5, 5))),
                'memory': min(100, max(0, latest_metrics.memory_usage + random.uniform(-3, 3))),
                'disk': latest_metrics.disk_usage,
                'network_in': latest_metrics.network_in + random.uniform(-10, 10),
                'network_out': latest_metrics.network_out + random.uniform(-5, 5),
                'active_users': latest_metrics.active_users + random.randint(-5, 10),
                'requests_per_second': latest_metrics.requests_per_second + random.uniform(-20, 20),
                'response_time': latest_metrics.response_time + random.uniform(-50, 50),
                'timestamp': timezone.now().isoformat()
            }
        else:
            # Generate simulated real-time data
            data = {
                'cpu': round(random.uniform(20, 80), 1),
                'memory': round(random.uniform(40, 90), 1), 
                'disk': round(random.uniform(45, 75), 1),
                'network_in': round(random.uniform(10, 100), 1),
                'network_out': round(random.uniform(5, 50), 1),
                'active_users': random.randint(50, 200),
                'requests_per_second': round(random.uniform(50, 150), 1),
                'response_time': round(random.uniform(80, 300), 1),
                'timestamp': timezone.now().isoformat()
            }
        
        return JsonResponse(data)
    
    return JsonResponse({'error': 'GET method required'})


def api_sales_by_region(request):
    """API endpoint for sales by region chart data"""
    if request.method == 'GET':
        # Get sales data grouped by region
        sales_data = []
        
        # Get latest period data for each region
        regions = SaleByRegion.objects.values('region').distinct()
        
        for region_data in regions:
            region_name = region_data['region']
            latest_sale = SaleByRegion.objects.filter(region=region_name).first()
            
            if latest_sale:
                sales_data.append({
                    'region': latest_sale.region,
                    'country': latest_sale.country,
                    'sales_amount': float(latest_sale.sales_amount),
                    'units_sold': latest_sale.units_sold,
                    'growth_rate': latest_sale.growth_rate,
                    'period': latest_sale.period_start.isoformat()
                })
        
        return JsonResponse({
            'regions': sales_data,
            'total_sales': sum(item['sales_amount'] for item in sales_data),
            'total_units': sum(item['units_sold'] for item in sales_data)
        })
    
    return JsonResponse({'error': 'GET method required'})


def api_activity_feed(request):
    """API endpoint for live activity feed"""
    if request.method == 'GET':
        # Get recent activities
        activities = ActivityFeed.objects.select_related('user')[:20]
        
        activity_data = []
        for activity in activities:
            activity_data.append({
                'id': activity.id,
                'action_type': activity.action_type,
                'description': activity.description,
                'user': activity.user.username if activity.user else 'System',
                'timestamp': activity.timestamp.isoformat(),
                'time_ago': calculate_time_ago(activity.timestamp),
                'object_type': activity.object_type,
                'ip_address': activity.ip_address
            })
        
        return JsonResponse({'activities': activity_data})
    
    return JsonResponse({'error': 'GET method required'})


def api_gallery_items(request):
    """API endpoint for gallery items"""
    if request.method == 'GET':
        category = request.GET.get('category', None)
        
        items = GalleryItem.objects.select_related('created_by')
        
        if category:
            items = items.filter(category=category)
        
        items = items[:12]  # Limit for performance
        
        gallery_data = []
        for item in items:
            gallery_data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'image_url': item.image_display_url,
                'category': item.category,
                'is_featured': item.is_featured,
                'created_by': item.created_by.username,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({'items': gallery_data})
    
    return JsonResponse({'error': 'GET method required'})


def api_file_manager(request):
    """API endpoint for file manager"""
    if request.method == 'GET':
        folder = request.GET.get('folder', 'root')
        
        files = FileManager.objects.filter(folder=folder).select_related('uploaded_by')
        
        file_data = []
        for file_obj in files:
            file_data.append({
                'id': file_obj.id,
                'name': file_obj.name,
                'file_type': file_obj.file_type,
                'formatted_size': file_obj.formatted_size,
                'mime_type': file_obj.mime_type,
                'folder': file_obj.folder,
                'is_public': file_obj.is_public,
                'download_count': file_obj.download_count,
                'uploaded_by': file_obj.uploaded_by.username,
                'uploaded_at': file_obj.uploaded_at.isoformat()
            })
        
        return JsonResponse({'files': file_data, 'current_folder': folder})
    
    return JsonResponse({'error': 'GET method required'})


def api_dynamic_tabs(request):
    """API endpoint for dynamic tabs"""
    if request.method == 'GET':
        tabs = DynamicTab.objects.filter(is_active=True).order_by('order')
        
        tab_data = []
        for tab in tabs:
            tab_data.append({
                'id': tab.id,
                'title': tab.title,
                'content': tab.content,
                'icon': tab.icon,
                'is_active': tab.is_active,
                'order': tab.order
            })
        
        return JsonResponse({'tabs': tab_data})
    
    return JsonResponse({'error': 'GET method required'})


def api_drag_drop_items(request):
    """API endpoint for drag & drop sortable items"""
    if request.method == 'GET':
        category = request.GET.get('category', 'tasks')
        
        items = DragDropItem.objects.filter(category=category).order_by('order')
        
        item_data = []
        for item in items:
            item_data.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'category': item.category,
                'order': item.order,
                'color': item.color,
                'icon': item.icon,
                'created_by': item.created_by.username
            })
        
        return JsonResponse({'items': item_data, 'category': category})
    
    elif request.method == 'POST':
        # Handle position updates
        try:
            data = json.loads(request.body)
            item_ids = data.get('item_ids', [])
            
            # Update positions based on new order
            for index, item_id in enumerate(item_ids):
                DragDropItem.objects.filter(id=item_id).update(order=index + 1)
            
            return JsonResponse({'success': True, 'message': 'Order updated successfully'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Invalid method'})


def calculate_time_ago(timestamp):
    """Helper function to calculate human-readable time ago"""
    from django.utils import timezone
    
    now = timezone.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f'{diff.days} days ago'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hours ago'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minutes ago'
    else:
        return 'Just now'
