from django.contrib import admin
from .models import CaseAnalytic, RevenueAnalytic

@admin.register(CaseAnalytic)
class CaseAnalyticAdmin(admin.ModelAdmin):
    list_display = ('case', 'metric_type', 'metric_value', 'metric_date', 'user')
    list_filter = ('metric_type', 'metric_date', 'created_at')
    search_fields = ('case__reference', 'case__title', 'user__email')
    ordering = ('-metric_date',)

@admin.register(RevenueAnalytic)
class RevenueAnalyticAdmin(admin.ModelAdmin):
    list_display = ('user', 'period_start', 'period_end', 'total_revenue', 'net_profit')
    list_filter = ('period_start', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-period_start',)