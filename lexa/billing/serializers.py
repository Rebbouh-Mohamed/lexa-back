# serializers.py
from rest_framework import serializers
from .models import BillingInfo, Invoice, InvoiceItem, Payment, Expense,Case
from django.utils import timezone
class BillingInfoSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BillingInfo
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class InvoiceItemSerializer(serializers.ModelSerializer):
    # Map frontend fields to model fields
    rate = serializers.DecimalField(source='unit_price', max_digits=12, decimal_places=2)
    amount = serializers.DecimalField(source='total_price', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'rate', 'amount', 'service_date']
        
    def validate(self, data):
        # Calculate total_price automatically
        quantity = data.get('quantity', 1)
        unit_price = data.get('unit_price', 0)
        data['total_price'] = quantity * unit_price
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ['user']
        read_only_fields = ['created_at']

class InvoiceSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    items = InvoiceItemSerializer(many=True, required=False)
    payments = PaymentSerializer(many=True, read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at', 'amount_paid']

    def validate_case(self, value):
        if not Case.objects.filter(id=value.id, user=self.context['request'].user).exists():
            raise serializers.ValidationError("Invalid case or you don't have permission to access it.")
        return value

    def validate_status(self, value):
        if value == 'overdue':
            due_date = self.initial_data.get('due_date')
            if due_date and due_date >= str(timezone.now().date()):
                raise serializers.ValidationError("Invoice cannot be marked overdue before the due date.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        subtotal = sum(item.get('quantity', 1) * item.get('unit_price', 0) for item in items_data)
        tax_rate = validated_data.get('tax_rate', 19.00)
        tax_amount = (subtotal * tax_rate) / 100
        total_amount = subtotal + tax_amount

        validated_data.update({
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount
        })

        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            item_data['total_price'] = item_data.get('quantity', 1) * item_data.get('unit_price', 0)
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items_data is not None:
            instance.items.all().delete()
            subtotal = sum(item.get('quantity', 1) * item.get('unit_price', 0) for item in items_data)
            tax_rate = instance.tax_rate
            tax_amount = (subtotal * tax_rate) / 100
            total_amount = subtotal + tax_amount

            instance.subtotal = subtotal
            instance.tax_amount = tax_amount
            instance.total_amount = total_amount

            for item_data in items_data:
                item_data['total_price'] = item_data.get('quantity', 1) * item_data.get('unit_price', 0)
                InvoiceItem.objects.create(invoice=instance, **item_data)

        instance.save()
        return instance

class ExpenseSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['user', 'created_at']