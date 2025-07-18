# Generated by Django 5.2.3 on 2025-06-18 15:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_billinginfo_cleint_name'),
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billinginfo',
            name='cleint_name',
        ),
        migrations.AddField(
            model_name='billinginfo',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AddField(
            model_name='billinginfo',
            name='client_name',
            field=models.CharField(default='client', max_length=200),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='case',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='cases.case'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='client_address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='tax_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
