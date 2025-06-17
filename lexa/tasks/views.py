from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.utils import timezone
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'priority', 'status', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related(
            'case', 'assigned_to', 'created_by'
        )
    
    def perform_create(self, serializer):
        print("Request data:", self.request.data)  # Debug print
        serializer.save(
            user=self.request.user,
            created_by=self.request.user,
            assigned_to=self.request.user,  # Default to creator
        )

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def task_dashboard(request):
    """Get task dashboard statistics"""
    user_tasks = Task.objects.filter(user=request.user)
    
    dashboard = {
        'total_tasks': user_tasks.count(),
        'pending_tasks': user_tasks.filter(status='pending').count(),
        'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
        'completed_tasks': user_tasks.filter(status='completed').count(),
        'overdue_tasks': user_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count(),
        'due_today': user_tasks.filter(
            due_date__date=timezone.now().date(),
            status__in=['pending', 'in_progress']
        ).count(),
        'due_this_week': user_tasks.filter(
            due_date__range=[
                timezone.now(),
                timezone.now() + timezone.timedelta(days=7)
            ],
            status__in=['pending', 'in_progress']
        ).count(),
        'tasks_by_priority': user_tasks.values('priority').annotate(
            count=Count('id')
        ),
        'tasks_by_status': user_tasks.values('status').annotate(
            count=Count('id')
        ),
        'recent_tasks': TaskSerializer(
            user_tasks.order_by('-created_at')[:5], many=True
        ).data
    }
    
    return Response(dashboard)