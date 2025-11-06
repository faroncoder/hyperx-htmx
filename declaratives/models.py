from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Task(models.Model):
    """Sample model for showcasing HyperX reactive CRUD operations"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High')
    ], default='medium')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('declaratives:task_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    """Sample model for live commenting system"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.task.title}'


class LiveMetric(models.Model):
    """Sample model for real-time dashboard metrics"""
    name = models.CharField(max_length=100)
    value = models.IntegerField()
    unit = models.CharField(max_length=20, default='count')
    category = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name}: {self.value} {self.unit}'


class SystemPerformance(models.Model):
    """System performance metrics for dashboard"""
    cpu_usage = models.FloatField(help_text="CPU usage percentage")
    memory_usage = models.FloatField(help_text="Memory usage percentage") 
    disk_usage = models.FloatField(help_text="Disk usage percentage")
    network_in = models.FloatField(help_text="Network input in MB/s")
    network_out = models.FloatField(help_text="Network output in MB/s")
    active_users = models.IntegerField(default=0)
    requests_per_second = models.FloatField(default=0.0)
    response_time = models.FloatField(help_text="Average response time in ms")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'Performance {self.timestamp.strftime("%H:%M:%S")}'


class SaleByRegion(models.Model):
    """Sales data by geographical region"""
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True)
    sales_amount = models.DecimalField(max_digits=12, decimal_places=2)
    units_sold = models.IntegerField(default=0)
    growth_rate = models.FloatField(help_text="Percentage growth", null=True, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sales_amount']
        unique_together = ['region', 'period_start', 'period_end']
    
    def __str__(self):
        return f'{self.region}: ${self.sales_amount:,.2f}'


class ActivityFeed(models.Model):
    """Live activity feed for dashboard"""
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('create', 'Created Item'),
        ('update', 'Updated Item'),
        ('delete', 'Deleted Item'),
        ('comment', 'Added Comment'),
        ('share', 'Shared Item'),
        ('like', 'Liked Item'),
        ('purchase', 'Made Purchase'),
        ('upload', 'Uploaded File'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.user.username} {self.get_action_type_display()} - {self.timestamp.strftime("%H:%M:%S")}'


class GalleryItem(models.Model):
    """Gallery items for carousel & gallery components"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="External image URL")
    category = models.CharField(max_length=50, default='general')
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def image_display_url(self):
        return self.image.url if self.image else self.image_url


class FileManager(models.Model):
    """File manager for upload/organization"""
    FILE_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    folder = models.CharField(max_length=255, default='root')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['folder', 'name']
    
    def __str__(self):
        return f'{self.folder}/{self.name}'
    
    @property
    def formatted_size(self):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"


class DynamicTab(models.Model):
    """Dynamic tabs content"""
    title = models.CharField(max_length=100)
    content = models.TextField()
    icon = models.CharField(max_length=50, default='file-text', help_text="Feather icon name")
    is_active = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title


class WizardStep(models.Model):
    """Multi-step wizard configuration"""
    wizard_name = models.CharField(max_length=100)
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_fields = models.JSONField(default=dict, help_text="Form field configuration")
    validation_rules = models.JSONField(default=dict, blank=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['wizard_name', 'step_number']
        unique_together = ['wizard_name', 'step_number']
    
    def __str__(self):
        return f'{self.wizard_name} - Step {self.step_number}: {self.title}'


class WizardSession(models.Model):
    """Track wizard progress for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wizard_name = models.CharField(max_length=100)
    current_step = models.PositiveIntegerField(default=1)
    step_data = models.JSONField(default=dict, help_text="Data collected from each step")
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'wizard_name']
    
    def __str__(self):
        return f'{self.user.username} - {self.wizard_name} (Step {self.current_step})'


class DragDropItem(models.Model):
    """Items for drag & drop sorting demonstration"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    icon = models.CharField(max_length=50, default='move', help_text="Feather icon name")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return f'{self.category}: {self.name}'
