"""
Management command to populate sample data for HyperX dynamic components.
This creates realistic sample data for all the new models to enable testing.
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from declaratives.models import (
    SystemPerformance,
    SaleByRegion, 
    ActivityFeed,
    GalleryItem,
    FileManager,
    DynamicTab,
    WizardStep,
    WizardSession,
    DragDropItem
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample data for HyperX dynamic components'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            SystemPerformance.objects.all().delete()
            SaleByRegion.objects.all().delete()
            ActivityFeed.objects.all().delete()
            GalleryItem.objects.all().delete()
            FileManager.objects.all().delete()
            DynamicTab.objects.all().delete()
            WizardStep.objects.all().delete()
            WizardSession.objects.all().delete()
            DragDropItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()

        self.stdout.write('Creating sample data...')

        # Create SystemPerformance data
        self.create_system_performance_data()
        
        # Create SaleByRegion data
        self.create_sales_data()
        
        # Create ActivityFeed data
        self.create_activity_feed_data(user)
        
        # Create GalleryItem data
        self.create_gallery_data(user)
        
        # Create FileManager data
        self.create_file_manager_data(user)
        
        # Create DynamicTab data
        self.create_dynamic_tabs_data(user)
        
        # Create Wizard data
        self.create_wizard_data()
        
        # Create DragDropItem data
        self.create_drag_drop_data(user)

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_system_performance_data(self):
        """Create realistic system performance metrics"""
        self.stdout.write('Creating system performance data...')
        
        # Create data points for the last 24 hours
        base_time = timezone.now() - timedelta(hours=24)
        
        for i in range(288):  # Every 5 minutes for 24 hours
            timestamp = base_time + timedelta(minutes=i * 5)
            
            # Generate realistic fluctuating data
            cpu_base = 35 + random.randint(-15, 25)
            memory_base = 60 + random.randint(-20, 30)
            network_in = random.randint(10, 100)
            network_out = random.randint(5, 50)
            
            SystemPerformance.objects.create(
                cpu_usage=max(0, min(100, cpu_base)),
                memory_usage=max(0, min(100, memory_base)),
                disk_usage=random.randint(45, 75),
                network_in=network_in,
                network_out=network_out,
                active_users=random.randint(50, 200),
                requests_per_second=round(random.uniform(10, 100), 2),
                response_time=round(random.uniform(50, 500), 2)
            )
        
        self.stdout.write(f'  Created {SystemPerformance.objects.count()} system performance entries')

    def create_sales_data(self):
        """Create sales data by region"""
        self.stdout.write('Creating sales by region data...')
        
        regions = [
            ('North America', 'US', '#3b82f6'),
            ('Europe', 'EU', '#10b981'),
            ('Asia Pacific', 'AP', '#f59e0b'),
            ('South America', 'SA', '#ef4444'),
            ('Middle East', 'ME', '#8b5cf6'),
            ('Africa', 'AF', '#06b6d4')
        ]
        
        for region_name, region_code, color in regions:
            # Create monthly data for the last 12 months
            for month_offset in range(12):
                date = timezone.now().replace(day=1) - timedelta(days=30 * month_offset)
                
                # Generate realistic sales data with seasonal variations
                base_sales = random.randint(50000, 150000)
                seasonal_factor = 1.2 if month_offset < 3 else 0.9  # Recent months higher
                sales_amount = int(base_sales * seasonal_factor * random.uniform(0.8, 1.2))
                
                SaleByRegion.objects.create(
                    region=region_name,
                    country=region_code,
                    sales_amount=sales_amount,
                    units_sold=random.randint(100, 1000),
                    period_start=date,
                    period_end=date.replace(day=28),  # End of month approximation
                    growth_rate=round(random.uniform(-5, 15), 1)
                )
        
        self.stdout.write(f'  Created {SaleByRegion.objects.count()} sales entries')

    def create_activity_feed_data(self, user):
        """Create activity feed entries"""
        self.stdout.write('Creating activity feed data...')
        
        activities = [
            ('user_login', 'User logged in', 'info'),
            ('file_upload', 'File uploaded successfully', 'success'),
            ('system_alert', 'System maintenance scheduled', 'warning'),
            ('data_export', 'Data export completed', 'success'),
            ('user_registration', 'New user registered', 'info'),
            ('backup_completed', 'System backup completed', 'success'),
            ('security_update', 'Security patch applied', 'warning'),
            ('performance_alert', 'High CPU usage detected', 'error'),
            ('task_completed', 'Scheduled task completed', 'success'),
            ('maintenance_start', 'Maintenance window started', 'warning')
        ]
        
        # Create entries for the last 7 days
        for i in range(50):
            activity_type, description, level = random.choice(activities)
            timestamp = timezone.now() - timedelta(
                hours=random.randint(1, 168),  # Last 7 days
                minutes=random.randint(0, 59)
            )
            
            # Only use valid action types from our model
            valid_actions = [choice[0] for choice in ActivityFeed.ACTION_TYPES]
            if activity_type in ['user_login', 'file_upload']:
                action = 'login' if activity_type == 'user_login' else 'upload'
            else:
                action = random.choice(valid_actions)
                
            ActivityFeed.objects.create(
                action_type=action,
                description=description,
                user=user,
                object_id=random.randint(1, 100) if random.choice([True, False]) else None,
                object_type=random.choice(['task', 'file', 'comment', 'user']) if random.choice([True, False]) else '',
                ip_address=f'192.168.1.{random.randint(1, 255)}',
                user_agent='Mozilla/5.0 (compatible; HyperX/1.0)'
            )
        
        self.stdout.write(f'  Created {ActivityFeed.objects.count()} activity feed entries')

    def create_gallery_data(self, user):
        """Create gallery items"""
        self.stdout.write('Creating gallery data...')
        
        categories = ['Nature', 'Technology', 'Architecture', 'Art', 'People', 'Travel']
        
        for i in range(20):
            category = random.choice(categories)
            
            GalleryItem.objects.create(
                title=f'Sample Image {i+1}',
                description=f'Beautiful {category.lower()} photo from our collection',
                image_url=f'https://picsum.photos/800/600?random={i+1}',
                category=category,
                created_by=user,
                is_featured=random.choice([True, False]),
                order=i + 1
            )
        
        self.stdout.write(f'  Created {GalleryItem.objects.count()} gallery items')

    def create_file_manager_data(self, user):
        """Create file manager entries"""
        self.stdout.write('Creating file manager data...')
        
        file_types = [
            ('document.pdf', 'application/pdf', 'document'),
            ('presentation.pptx', 'application/vnd.ms-powerpoint', 'presentation'),
            ('spreadsheet.xlsx', 'application/vnd.ms-excel', 'spreadsheet'),
            ('image.jpg', 'image/jpeg', 'image'),
            ('archive.zip', 'application/zip', 'archive'),
            ('video.mp4', 'video/mp4', 'video'),
            ('audio.mp3', 'audio/mpeg', 'audio'),
            ('code.py', 'text/x-python', 'code')
        ]
        
        folders = ['Documents', 'Images', 'Videos', 'Projects', 'Archives']
        
        # Create files directly (no folder hierarchy for now)
        for i in range(25):
            filename, mime_type, file_type = random.choice(file_types)
            folder_name = random.choice(folders)
            
            FileManager.objects.create(
                name=f'{file_type}_{i+1}_{filename}',
                file_type=file_type,
                file_size=random.randint(1024, 50000000),  # 1KB to 50MB
                mime_type=mime_type,
                folder=folder_name,
                uploaded_by=user,
                is_public=random.choice([True, False])
            )
        
        self.stdout.write(f'  Created {FileManager.objects.count()} file manager entries')

    def create_dynamic_tabs_data(self, user=None):
        """Create dynamic tabs"""
        self.stdout.write('Creating dynamic tabs data...')
        
        tabs_data = [
            ('overview', 'Overview', 'Welcome to the HyperX dashboard overview', '<div class="p-4"><h3>Dashboard Overview</h3><p>This is the main overview tab with key metrics and summaries.</p></div>', 1),
            ('analytics', 'Analytics', 'Detailed analytics and reports', '<div class="p-4"><h3>Analytics Dashboard</h3><p>View detailed analytics, charts, and performance metrics here.</p></div>', 2),
            ('settings', 'Settings', 'System and user settings', '<div class="p-4"><h3>Settings Panel</h3><p>Configure your system preferences and user settings.</p></div>', 3),
            ('reports', 'Reports', 'Generate and view reports', '<div class="p-4"><h3>Reports Center</h3><p>Generate, view, and download various system reports.</p></div>', 4),
            ('help', 'Help', 'Documentation and support', '<div class="p-4"><h3>Help Center</h3><p>Find documentation, tutorials, and get support.</p></div>', 5)
        ]
        
        for tab_id, title, description, content, order in tabs_data:
            DynamicTab.objects.create(
                title=title,
                content=content,
                is_active=order == 1,
                order=order,
                icon=f'{tab_id}' if tab_id != 'overview' else 'home',
                created_by=user
            )
        
        self.stdout.write(f'  Created {DynamicTab.objects.count()} dynamic tabs')

    def create_wizard_data(self):
        """Create wizard steps"""
        self.stdout.write('Creating wizard data...')
        
        wizard_steps = [
            ('welcome', 'Welcome', 'Welcome to the setup wizard', 
             '<div class="text-center"><h3>Welcome!</h3><p>This wizard will guide you through the initial setup process.</p></div>', 
             1, True),
            ('account', 'Account Setup', 'Configure your account settings',
             '<div><h4>Account Information</h4><form><div class="mb-3"><label class="form-label">Username</label><input type="text" class="form-control"></div><div class="mb-3"><label class="form-label">Email</label><input type="email" class="form-control"></div></form></div>',
             2, True),
            ('preferences', 'Preferences', 'Set your preferences',
             '<div><h4>User Preferences</h4><form><div class="mb-3"><label class="form-label">Theme</label><select class="form-select"><option>Light</option><option>Dark</option></select></div><div class="mb-3"><label class="form-label">Language</label><select class="form-select"><option>English</option><option>Spanish</option></select></div></form></div>',
             3, True),
            ('notifications', 'Notifications', 'Configure notification settings',
             '<div><h4>Notification Settings</h4><form><div class="form-check"><input class="form-check-input" type="checkbox" checked><label class="form-check-label">Email notifications</label></div><div class="form-check"><input class="form-check-input" type="checkbox"><label class="form-check-label">SMS notifications</label></div></form></div>',
             4, False),
            ('complete', 'Complete', 'Setup complete!',
             '<div class="text-center"><h3>Setup Complete!</h3><p>Your account has been configured successfully.</p></div>',
             5, True)
        ]
        
        for step_id, title, description, content, order, required in wizard_steps:
            WizardStep.objects.create(
                wizard_name='setup_wizard',
                step_number=order,
                title=title,
                description=description,
                form_fields={
                    'content': content,
                    'step_id': step_id
                },
                is_required=required,
                validation_rules={
                    'required_fields': ['username', 'email'] if step_id == 'account' else [],
                    'min_length': 3 if step_id == 'account' else 0
                } if step_id == 'account' else {}
            )
        
        self.stdout.write(f'  Created {WizardStep.objects.count()} wizard steps')

    def create_drag_drop_data(self, user):
        """Create drag-drop sortable items"""
        self.stdout.write('Creating drag-drop data...')
        
        categories = ['tasks', 'priorities', 'features']
        
        # Create tasks list
        tasks = [
            'Review project documentation',
            'Update user interface design',
            'Implement new features',
            'Fix reported bugs',
            'Write unit tests',
            'Deploy to staging environment',
            'Conduct user testing',
            'Optimize performance'
        ]
        
        for i, task in enumerate(tasks):
            DragDropItem.objects.create(
                name=task,
                description=f'Task: {task}',
                category='tasks',
                order=i + 1,
                created_by=user,
                color=random.choice(['#3b82f6', '#10b981', '#f59e0b', '#ef4444']),
                icon='check-square'
            )
        
        # Create priority items
        priorities = ['Critical Bug Fixes', 'User Experience', 'Performance', 'Security', 'Documentation']
        
        for i, priority in enumerate(priorities):
            DragDropItem.objects.create(
                name=priority,
                description=f'Priority: {priority}',
                category='priorities',
                order=i + 1,
                created_by=user,
                color=random.choice(['#dc2626', '#ea580c', '#d97706', '#65a30d']),
                icon='flag'
            )
        
        # Create feature items
        features = ['Dashboard Widgets', 'User Management', 'Reporting System', 'API Integration', 'Mobile App']
        
        for i, feature in enumerate(features):
            DragDropItem.objects.create(
                name=feature,
                description=f'Feature: {feature}',
                category='features',
                order=i + 1,
                created_by=user,
                color=random.choice(['#7c3aed', '#2563eb', '#0891b2', '#059669']),
                icon='layers'
            )
        
        self.stdout.write(f'  Created {DragDropItem.objects.count()} drag-drop items')