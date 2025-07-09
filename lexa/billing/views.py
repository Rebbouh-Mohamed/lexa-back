from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import BillingInfo, Invoice, InvoiceItem, Payment, Expense
from .serializers import (
    BillingInfoSerializer, InvoiceSerializer, InvoiceItemSerializer,
    PaymentSerializer, ExpenseSerializer
)

class BillingInfoListCreateView(generics.ListCreateAPIView):
    serializer_class = BillingInfoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'payment_status']
    search_fields = ['invoice_number', 'case__reference', 'case__title']
    ordering_fields = ['invoice_date', 'due_date', 'amount']

    def get_queryset(self):
        return BillingInfo.objects.filter(user=self.request.user).select_related('case')

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(request.data)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BillingInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BillingInfoSerializer

    def get_queryset(self):
        return BillingInfo.objects.filter(user=self.request.user)

# class InvoiceListCreateView(generics.ListCreateAPIView):
#     serializer_class = InvoiceSerializer
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_fields = ['case', 'status']
#     search_fields = ['invoice_number', 'client_name', 'case__reference']
#     ordering_fields = ['invoice_date', 'due_date', 'total_amount']

#     def get_queryset(self):
#         return Invoice.objects.filter(user=self.request.user).select_related('case')

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'status']
    search_fields = ['invoice_number', 'client_name', 'case__reference', 'case__title']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).select_related('case')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'category', 'is_reimbursable', 'is_reimbursed']
    search_fields = ['description', 'case__reference']
    ordering_fields = ['expense_date', 'amount']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).select_related('case')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def revenue_analytics(request):
    """Get revenue analytics for the user"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to current year if no dates provided
    if not start_date or not end_date:
        now = timezone.now()
        start_date = now.replace(month=1, day=1).date()
        end_date = now.date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get invoices in date range
    invoices = Invoice.objects.filter(
        user=request.user,
        invoice_date__range=[start_date, end_date]
    )
    
    # Get expenses in date range
    expenses = Expense.objects.filter(
        user=request.user,
        expense_date__range=[start_date, end_date]
    )
    
    # Calculate metrics
    total_revenue = invoices.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    paid_revenue = invoices.filter(
        status='paid'
    ).aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    outstanding_amount = invoices.filter(
        status__in=['sent', 'partially_paid']
    ).aggregate(
        total=Sum('outstanding_amount')
    )['total'] or 0
    
    analytics = {
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'revenue': {
            'total_invoiced': float(total_revenue),
            'total_paid': float(paid_revenue),
            'outstanding': float(outstanding_amount),
            'net_profit': float(paid_revenue - total_expenses)
        },
        'expenses': {
            'total_expenses': float(total_expenses)
        },
        'invoices': {
            'total_count': invoices.count(),
            'paid_count': invoices.filter(status='paid').count(),
            'overdue_count': invoices.filter(
                status__in=['sent', 'partially_paid'],
                due_date__lt=timezone.now().date()
            ).count()
        },
        'cases': {
            'case_count': invoices.values('case').distinct().count(),
            'avg_case_value': float(total_revenue / max(invoices.values('case').distinct().count(), 1))
        }
    }
    
    return Response(analytics)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_invoice_payment(request, invoice_id):
    """Add a payment to an invoice"""
    try:
        invoice = Invoice.objects.get(id=invoice_id, user=request.user)
    except Invoice.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Create payment
    payment = Payment.objects.create(
        invoice=invoice,
        amount=request.data.get('amount'),
        payment_date=request.data.get('payment_date'),
        payment_method=request.data.get('payment_method'),
        reference_number=request.data.get('reference_number', ''),
        notes=request.data.get('notes', ''),
        user=request.user
    )
    
    # Update invoice
    invoice.amount_paid += payment.amount
    if invoice.amount_paid >= invoice.total_amount:
        invoice.status = 'paid'
        invoice.payment_date = payment.payment_date
    elif invoice.amount_paid > 0:
        invoice.status = 'partially_paid'
    
    invoice.save()
    
    return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
