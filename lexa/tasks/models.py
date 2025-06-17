from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from cases.models import Case

User = get_user_model()

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('on_hold', _('On Hold')),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    
    # Task details
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks',null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Progress tracking
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    
    # Notifications
    reminder_sent = models.BooleanField(default=False)
    reminder_date = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    tags = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    
    # User relationship (for filtering)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-due_date', '-priority']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        from django.utils import timezone
        return (self.due_date and 
                self.due_date < timezone.now() and 
                self.status not in ['completed', 'cancelled'])

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
        from django.utils import timezone
        delta = self.due_date.date() - timezone.now().date()
        return delta.days

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.task.title}"