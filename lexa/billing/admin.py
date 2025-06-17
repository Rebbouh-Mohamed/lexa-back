from django.contrib import admin
from .models import BillingInfo, Invoice, InvoiceItem, Payment, Expense

@admin.register(BillingInfo)
class BillingInfoAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'case', 'fee_type', 'amount', 'payment_status', 'invoice_date')
    list_filter = ('fee_type', 'payment_status', 'invoice_date', 'created_at')
    search_fields = ('invoice_number', 'case__reference', 'case__title')
    ordering = ('-invoice_date',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client_name', 'status', 'total_amount', 'invoice_date', 'due_date')
    list_filter = ('status', 'invoice_date', 'due_date')
    search_fields = ('invoice_number', 'client_name', 'case__reference')
    ordering = ('-invoice_date',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total_price')
    search_fields = ('description', 'invoice__invoice_number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method', 'reference_number')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('invoice__invoice_number', 'reference_number')
    ordering = ('-payment_date',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'case', 'category', 'amount', 'expense_date', 'is_reimbursed')
    list_filter = ('category', 'is_reimbursable', 'is_reimbursed', 'expense_date')
    search_fields = ('description', 'case__reference')
    ordering = ('-expense_date',)