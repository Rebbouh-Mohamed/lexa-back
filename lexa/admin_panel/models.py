from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class AdminAction(models.Model):
    ACTION_TYPES = [
        ('user_approved', _('User Approved')),
        ('user_blocked', _('User Blocked')),
        ('user_deleted', _('User Deleted')),
        ('user_suspended', _('User Suspended')),
        ('subscription_updated', _('Subscription Updated')),
        ('system_maintenance', _('System Maintenance')),
        ('data_export', _('Data Export')),
        ('data_import', _('Data Import')),
        ('security_alert', _('Security Alert')),
    ]

    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_received')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    reason = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    # IP tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Admin Action')
        verbose_name_plural = _('Admin Actions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.admin.get_full_name()} - {self.get_action_type_display()}"

class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False)  # For passwords, API keys, etc.
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('System Configuration')
        verbose_name_plural = _('System Configurations')

    def __str__(self):
        return self.key

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('trial', _('Trial')),
        ('basic', _('Basic')),
        ('professional', _('Professional')),
        ('enterprise', _('Enterprise')),
    ]
    
    STATUS_CHOICES = [
        ('trial', _('Trial')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('cancelled', _('Cancelled')),
        ('expired', _('Expired')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan_name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    trial_end_date = models.DateField(null=True, blank=True)
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='DZD')
    
    # Features
    max_cases = models.PositiveIntegerField(default=10)
    max_documents = models.PositiveIntegerField(default=100)
    max_storage_gb = models.PositiveIntegerField(default=1)
    api_access = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    
    # Billing
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
    ], default='monthly')
    
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan_name}"

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and self.end_date >= timezone.now().date()

    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(0, delta.days)
        return 0