from django.urls import path
from . import views

urlpatterns = [
    # Billing Info
    # path('billing/', views.BillingInfoListCreateView.as_view(), name='billing_list_create'),
    path('billing/', views.InvoiceListCreateView.as_view(), name='billing_list_create'),

    path('billing/<int:pk>/', views.InvoiceDetailView.as_view(), name='billing_detail'),
    
    # Invoices
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:invoice_id>/payments/', views.add_invoice_payment, name='add_invoice_payment'),
    
    # Expenses
    path('expenses/', views.ExpenseListCreateView.as_view(), name='expense_list_create'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense_detail'),
    
    # Analytics
    path('analytics/revenue/', views.revenue_analytics, name='revenue_analytics'),
]
