from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'status', 'subscription_status', 'created_at')
    list_filter = ('role', 'status', 'subscription_status', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'bar_number')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'status', 'subscription_status', 'subscription_plan',
                      'phone', 'address', 'bar_number', 'wilaya', 'last_sign_in_at')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'law_firm', 'years_experience', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'law_firm')
    list_filter = ('years_experience', 'created_at')    