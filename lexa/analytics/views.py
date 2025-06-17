from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CaseAnalytic, RevenueAnalytic
from .serializers import CaseAnalyticSerializer, RevenueAnalyticSerializer
from cases.models import Case
from billing.models import Invoice, Expense

class CaseAnalyticListCreateView(generics.ListCreateAPIView):
    serializer_class = CaseAnalyticSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['case', 'metric_type']
    ordering_fields = ['metric_date', 'created_at']

    def get_queryset(self):
        return CaseAnalytic.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RevenueAnalyticListView(generics.ListAPIView):
    serializer_class = RevenueAnalyticSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['period_start', 'period_end']

    def get_queryset(self):
        return RevenueAnalytic.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def case_performance_analytics(request):
    """Get case performance analytics"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        # Default to last 12 months
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    user_cases = Case.objects.filter(user=request.user)
    
    # Case completion metrics
    completed_cases = user_cases.filter(
        close_date__range=[start_date, end_date]
    )
    
    # Calculate average case duration
    case_durations = []
    for case in completed_cases:
        if case.close_date and case.open_date:
            duration = (case.close_date - case.open_date).days
            case_durations.append(duration)
    
    avg_duration = sum(case_durations) / len(case_durations) if case_durations else 0
    
    # Revenue analytics
    invoices = Invoice.objects.filter(
        case__user=request.user,
        invoice_date__range=[start_date, end_date]
    )
    
    total_revenue = invoices.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    paid_revenue = invoices.filter(
        status='paid'
    ).aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    # Expense analytics
    expenses = Expense.objects.filter(
        case__user=request.user,
        expense_date__range=[start_date, end_date]
    )
    
    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Case type distribution
    case_type_stats = user_cases.filter(
        open_date__range=[start_date, end_date]
    ).values(
        'case_type__category_fr'
    ).annotate(
        count=Count('id')
    )
    
    # Monthly trends
    monthly_stats = []
    current_date = start_date
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        month_revenue = invoices.filter(
            invoice_date__range=[month_start, month_end]
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        month_cases = user_cases.filter(
            open_date__range=[month_start, month_end]
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(month_revenue),
            'cases_opened': month_cases
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    analytics = {
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'case_metrics': {
            'total_cases': user_cases.count(),
            'completed_cases': completed_cases.count(),
            'active_cases': user_cases.filter(
                status__in=['ouvert', 'en_cours_instruction']
            ).count(),
            'average_duration_days': round(avg_duration, 1),
            'case_type_distribution': list(case_type_stats)
        },
        'financial_metrics': {
            'total_revenue': float(total_revenue),
            'paid_revenue': float(paid_revenue),
            'total_expenses': float(total_expenses),
            'net_profit': float(paid_revenue - total_expenses),
            'average_case_value': float(total_revenue / max(completed_cases.count(), 1))
        },
        'monthly_trends': monthly_stats
    }
    
    return Response(analytics)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_revenue_report(request):
    """Generate comprehensive revenue report"""
    start_date = datetime.strptime(request.data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.data.get('end_date'), '%Y-%m-%d').date()
    
    # Calculate metrics
    user_cases = Case.objects.filter(user=request.user)
    invoices = Invoice.objects.filter(
        case__user=request.user,
        invoice_date__range=[start_date, end_date]
    )
    expenses = Expense.objects.filter(
        case__user=request.user,
        expense_date__range=[start_date, end_date]
    )
    
    total_revenue = invoices.aggregate(Sum('total_amount'))['total'] or 0
    paid_revenue = invoices.filter(status='paid').aggregate(Sum('amount_paid'))['total'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['total'] or 0
    
    cases_opened = user_cases.filter(open_date__range=[start_date, end_date]).count()
    cases_closed = user_cases.filter(close_date__range=[start_date, end_date]).count()
    
    # Calculate billable hours and success rate
    billable_hours = sum([
        float(billing.hours_worked) for billing in 
        user_cases.filter(
            billing_info__invoice_date__range=[start_date, end_date]
        ).values_list('billing_info__hours_worked', flat=True)
        if billing.hours_worked
    ]) if user_cases.exists() else 0
    
    avg_hourly_rate = paid_revenue / billable_hours if billable_hours > 0 else 0
    
    # Create or update revenue analytic record
    revenue_analytic, created = RevenueAnalytic.objects.update_or_create(
        user=request.user,
        period_start=start_date,
        period_end=end_date,
        defaults={
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': paid_revenue - total_expenses,
            'cases_opened': cases_opened,
            'cases_closed': cases_closed,
            'active_cases': user_cases.filter(
                status__in=['ouvert', 'en_cours_instruction']
            ).count(),
            'average_case_value': total_revenue / max(cases_closed, 1),
            'total_billable_hours': billable_hours,
            'average_hourly_rate': avg_hourly_rate,
            'success_rate': 85.0  # This would be calculated based on case outcomes
        }
    )
    
    serializer = RevenueAnalyticSerializer(revenue_analytic)
    return Response(serializer.data)