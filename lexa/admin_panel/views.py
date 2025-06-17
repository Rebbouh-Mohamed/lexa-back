from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from .models import AdminAction, SystemConfiguration, Subscription
from .serializers import (
    AdminUserSerializer, AdminActionSerializer, 
    SystemConfigurationSerializer, SubscriptionSerializer
)
from django.db import models

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'status', 'subscription_status', 'wilaya']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['created_at', 'last_sign_in_at', 'email']
    
    def get_queryset(self):
        return User.objects.all().order_by('-created_at')

class AdminActionListCreateView(generics.ListCreateAPIView):
    serializer_class = AdminActionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action_type', 'admin', 'target_user']
    search_fields = ['reason', 'admin__email', 'target_user__email']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return AdminAction.objects.select_related('admin', 'target_user').order_by('-created_at')

    def perform_create(self, serializer):
        # Get IP address and user agent from request
        ip_address = self.get_client_ip()
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        serializer.save(
            admin=self.request.user,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['plan_name', 'status', 'billing_cycle']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'end_date']

    def get_queryset(self):
        return Subscription.objects.select_related('user').order_by('-created_at')

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Subscription.objects.select_related('user')

@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_user(request, user_id):
    """Approve a pending user"""
    try:
        user = User.objects.get(id=user_id)
        user.status = 'active'
        user.save(update_fields=['status'])
        
        # Log admin action
        AdminAction.objects.create(
            admin=request.user,
            target_user=user,
            action_type='user_approved',
            reason=request.data.get('reason', 'User approved by admin'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'User approved successfully'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def block_user(request, user_id):
    """Block a user"""
    try:
        user = User.objects.get(id=user_id)
        user.status = 'blocked'
        user.save(update_fields=['status'])
        
        # Log admin action
        AdminAction.objects.create(
            admin=request.user,
            target_user=user,
            action_type='user_blocked',
            reason=request.data.get('reason', 'User blocked by admin'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'User blocked successfully'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """Get admin dashboard statistics"""
    stats = {
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(status='active').count(),
            'pending': User.objects.filter(status='pending').count(),
            'blocked': User.objects.filter(status='blocked').count(),
            'new_this_month': User.objects.filter(
                created_at__gte=timezone.now().replace(day=1)
            ).count()
        },
        'subscriptions': {
            'total': Subscription.objects.count(),
            'active': Subscription.objects.filter(status='active').count(),
            'trial': Subscription.objects.filter(status='trial').count(),
            'expired': Subscription.objects.filter(status='expired').count(),
            'revenue_this_month': Subscription.objects.filter(
                status='active',
                start_date__gte=timezone.now().replace(day=1)
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or 0
        },
        'activity': {
            'recent_actions': AdminActionSerializer(
                AdminAction.objects.order_by('-created_at')[:10], many=True
            ).data
        }
    }
    
    return Response(stats)