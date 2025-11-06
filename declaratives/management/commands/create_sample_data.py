from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from declaratives.models import Task, Comment


class Command(BaseCommand):
    help = 'Create sample data for HyperX Declaratives showcase'

    def handle(self, *args, **options):
        self.stdout.write("🎭 Creating HyperX Declaratives sample data...")
        
        # Create or get a demo user
        demo_user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'email': 'demo@hyperx.local'
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(f"✅ Created demo user: {demo_user.username}")
        
        # Sample tasks
        sample_tasks = [
            {
                'title': 'Build HyperX Dashboard',
                'description': 'Create a reactive dashboard using HTMX template tags',
                'priority': 'high',
                'completed': True
            },
            {
                'title': 'Implement Live Search',
                'description': 'Add real-time search functionality with debouncing',
                'priority': 'medium',
                'completed': True
            },
            {
                'title': 'Add Form Validation',
                'description': 'Real-time form validation using htmx_validate_field',
                'priority': 'medium',
                'completed': False
            },
            {
                'title': 'WebSocket Integration',
                'description': 'Connect WebSocket for real-time notifications',
                'priority': 'high',
                'completed': False
            },
            {
                'title': 'Polish UI Components',
                'description': 'Enhance styling and animations for better UX',
                'priority': 'low',
                'completed': False
            },
            {
                'title': 'Write Documentation',
                'description': 'Document all HyperX template tags and usage patterns',
                'priority': 'medium',
                'completed': False
            }
        ]
        
        created_tasks = 0
        for task_data in sample_tasks:
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                created_by=demo_user,
                defaults={
                    'description': task_data['description'],
                    'priority': task_data['priority'],
                    'completed': task_data['completed']
                }
            )
            if created:
                created_tasks += 1
                
                # Add some comments to completed tasks
                if task.completed:
                    Comment.objects.get_or_create(
                        task=task,
                        author=demo_user,
                        defaults={'content': 'Great work! This feature is working perfectly.'}
                    )
        
        self.stdout.write(f"✅ Created {created_tasks} sample tasks")
        
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(completed=True).count()
        
        self.stdout.write("")
        self.stdout.write("📊 Showcase Statistics:")
        self.stdout.write(f"   Total Tasks: {total_tasks}")
        self.stdout.write(f"   Completed: {completed_tasks}")
        self.stdout.write(f"   Pending: {total_tasks - completed_tasks}")
        self.stdout.write("")
        self.stdout.write("🚀 HyperX Declaratives showcase is ready!")
        self.stdout.write("   Visit: http://localhost:8000/declaratives/")
        
        if created:
            self.stdout.write("")
            self.stdout.write("🔐 Demo Login:")
            self.stdout.write("   Username: demo_user")
            self.stdout.write("   Password: demo123")