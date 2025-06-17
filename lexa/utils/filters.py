import django_filters
from django.db import models
from cases.models import Case, Audience
from documents.models import Document
from tasks.models import Task
from billing.models import Invoice, Expense

class CaseFilter(django_filters.FilterSet):
    open_date_after = django_filters.DateFilter(field_name='open_date', lookup_expr='gte')
    open_date_before = django_filters.DateFilter(field_name='open_date', lookup_expr='lte')
    close_date_after = django_filters.DateFilter(field_name='close_date', lookup_expr='gte')
    close_date_before = django_filters.DateFilter(field_name='close_date', lookup_expr='lte')
    amount_min = django_filters.NumberFilter(field_name='amount_in_dispute', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount_in_dispute', lookup_expr='lte')
    
    class Meta:
        model = Case
        fields = {
            'status': ['exact', 'in'],
            'priority': ['exact', 'in'],
            'jurisdiction': ['exact'],
            'case_type': ['exact'],
            'user': ['exact'],
        }

class DocumentFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    file_size_min = django_filters.NumberFilter(field_name='file_size', lookup_expr='gte')
    file_size_max = django_filters.NumberFilter(field_name='file_size', lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = {
            'case': ['exact'],
            'document_type': ['exact', 'in'],
            'template_type': ['exact', 'in'],
            'language': ['exact', 'in'],
            'is_final': ['exact'],
            'is_confidential': ['exact'],
        }

class TaskFilter(django_filters.FilterSet):
    due_date_after = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_before = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    overdue = django_filters.BooleanFilter(method='filter_overdue')
    completed_this_week = django_filters.BooleanFilter(method='filter_completed_this_week')
    
    class Meta:
        model = Task
        fields = {
            'case': ['exact'],
            'priority': ['exact', 'in'],
            'status': ['exact', 'in'],
            'assigned_to': ['exact'],
            'created_by': ['exact'],
        }