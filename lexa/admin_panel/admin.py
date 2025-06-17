from django.contrib import admin
from .models import AdminAction, SystemConfiguration, Subscription

@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action_type', 'target_user', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('admin__email', 'target_user__email', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'is_sensitive', 'updated_at')
    list_filter = ('is_sensitive', 'updated_at')
    search_fields = ('key', 'description')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'status', 'start_date', 'end_date', 'amount')
    list_filter = ('plan_name', 'status', 'billing_cycle')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
