# Generated by Django 5.2.3 on 2025-06-17 23:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_alter_invoice_amount_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billinginfo',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='billinginfo',
            name='fee_type',
        ),
    ]
