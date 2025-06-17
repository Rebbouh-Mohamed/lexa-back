from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('task_due', _('Task Due')),
        ('task_overdue', _('Task Overdue')),
        ('audience_reminder', _('Audience Reminder')),
        ('case_update', _('Case Update')),
        ('document_shared', _('Document Shared')),
        ('payment_received', _('Payment Received')),
        ('invoice_overdue', _('Invoice Overdue')),
        ('new_message', _('New Message')),
        ('system', _('System Notification')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Related objects
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Action URL
    action_url = models.URLField(blank=True)
    
    # Metadata
    data = models.JSONField(default=dict, blank=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_task_reminders = models.BooleanField(default=True)
    email_audience_reminders = models.BooleanField(default=True)
    email_case_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_document_shares = models.BooleanField(default=True)
    
    # In-app notifications
    app_task_reminders = models.BooleanField(default=True)
    app_audience_reminders = models.BooleanField(default=True)
    app_case_updates = models.BooleanField(default=True)
    app_payment_updates = models.BooleanField(default=True)
    app_document_shares = models.BooleanField(default=True)
    
    # SMS notifications (if implemented)
    sms_urgent_only = models.BooleanField(default=False)
    
    # Timing preferences
    daily_digest = models.BooleanField(default=True)
    daily_digest_time = models.TimeField(default='09:00:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.get_full_name()}"
