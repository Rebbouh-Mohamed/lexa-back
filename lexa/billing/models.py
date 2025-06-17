# billing/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from cases.models import Case

User = get_user_model()

class BillingInfo(models.Model):
    FEE_TYPE_CHOICES = [
        ('fixed', _('Fixed Fee')),
        ('hourly', _('Hourly Rate')),
        ('contingency', _('Contingency Fee')),
        ('retainer', _('Retainer')),
        ('success', _('Success Fee')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='billing_info')
    
    # Fee structure
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Additional costs
    advanced_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    court_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    administrative_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Algerian tax information
    nif = models.CharField(max_length=20, blank=True, help_text="Numéro d'Identification Fiscale")
    nis = models.CharField(max_length=20, blank=True, help_text="Numéro d'Identification Statistique")
    rc = models.CharField(max_length=20, blank=True, help_text="Registre de Commerce")
    tva = models.CharField(max_length=20, blank=True, help_text="Numéro TVA")
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Currency
    currency = models.CharField(max_length=3, default='DZD')
    
    # Notes
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_records')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Billing Information')
        verbose_name_plural = _('Billing Information')
        ordering = ['-invoice_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.case.reference}"

    @property
    def total_amount(self):
        """Calculate total amount including all fees and expenses"""
        base_amount = self.amount
        if self.fee_type == 'hourly' and self.hourly_rate:
            base_amount = self.hourly_rate * self.hours_worked
        
        return base_amount + self.advanced_expenses + self.court_fees + self.administrative_fees

    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from django.utils import timezone
        return self.payment_status == 'pending' and self.due_date < timezone.now().date()

class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]

    # Invoice identification
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    
    # Client information
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='invoices')
    client_name = models.CharField(max_length=200)
    client_address = models.TextField()
    client_email = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    
    # Invoice details
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.00)  # TVA 19% in Algeria
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Payment tracking
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Currency
    currency = models.CharField(max_length=3, default='DZD')
    
    # Additional information
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-invoice_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.client_name}"

    @property
    def outstanding_amount(self):
        """Calculate outstanding amount"""
        return self.total_amount - self.amount_paid

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone
        return self.status in ['sent', 'partially_paid'] and self.due_date < timezone.now().date()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    # For hourly billing
    hours_worked = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Date of service
    service_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')

    def __str__(self):
        return f"{self.description} - {self.total_price} {self.invoice.currency}"

    def save(self, *args, **kwargs):
        # Calculate total price automatically
        if self.hours_worked and self.hourly_rate:
            self.total_price = self.hours_worked * self.hourly_rate
        else:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('check', _('Check')),
        ('bank_transfer', _('Bank Transfer')),
        ('card', _('Credit/Debit Card')),
        ('online', _('Online Payment')),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Bank details (for transfers/checks)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"

class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('court_fees', _('Court Fees')),
        ('administrative', _('Administrative Fees')),
        ('travel', _('Travel Expenses')),
        ('expert_fees', _('Expert Fees')),
        ('translation', _('Translation Services')),
        ('postage', _('Postage and Shipping')),
        ('office_supplies', _('Office Supplies')),
        ('legal_research', _('Legal Research')),
        ('other', _('Other')),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=30, choices=EXPENSE_CATEGORIES)
    description = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    
    # Receipt tracking
    receipt_number = models.CharField(max_length=100, blank=True)
    receipt_file = models.FileField(upload_to='receipts/%Y/%m/', null=True, blank=True)
    
    # Reimbursement
    is_reimbursable = models.BooleanField(default=True)
    is_reimbursed = models.BooleanField(default=False)
    reimbursement_date = models.DateField(null=True, blank=True)
    
    # Currency
    currency = models.CharField(max_length=3, default='DZD')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency}"
