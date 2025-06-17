
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from cases.models import Case

User = get_user_model()

class CaseAnalytic(models.Model):
    METRIC_TYPES = [
        ('duration', _('Case Duration')),
        ('revenue', _('Revenue Generated')),
        ('client_satisfaction', _('Client Satisfaction')),
        ('complexity_score', _('Complexity Score')),
        ('success_rate', _('Success Rate')),
        ('time_spent', _('Time Spent')),
        ('document_count', _('Document Count')),
        ('audience_count', _('Audience Count')),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='analytics', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='case_analytics')
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    metric_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    metric_text = models.CharField(max_length=200, blank=True)
    metric_date = models.DateField()
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Case Analytic')
        verbose_name_plural = _('Case Analytics')
        ordering = ['-metric_date']

    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.metric_value}"

class RevenueAnalytic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_analytics')
    
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Case metrics
    cases_opened = models.PositiveIntegerField(default=0)
    cases_closed = models.PositiveIntegerField(default=0)
    active_cases = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_case_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    average_case_duration = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # in days
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    
    # Time tracking
    total_billable_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Revenue Analytic')
        verbose_name_plural = _('Revenue Analytics')
        unique_together = ['user', 'period_start', 'period_end']
        ordering = ['-period_start']

    def __str__(self):
        return f"Revenue Analytics {self.period_start} - {self.period_end}"
