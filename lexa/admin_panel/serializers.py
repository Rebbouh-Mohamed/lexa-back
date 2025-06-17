from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AdminAction, SystemConfiguration, Subscription

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'status', 'subscription_status', 'subscription_plan',
            'phone', 'wilaya', 'created_at', 'last_sign_in_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_sign_in_at']

class AdminActionSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    target_user_name = serializers.CharField(source='target_user.get_full_name', read_only=True)
    
    class Meta:
        model = AdminAction
        fields = '__all__'
        read_only_fields = ['admin', 'created_at']

class SystemConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'updated_by']

class SubscriptionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']