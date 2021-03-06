# Generated by Django 2.0.13 on 2019-10-09 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0059_auto_20191005_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorder',
            name='invoice_paid_to',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Paid to associate'), (2, 'Paid to organization.')], help_text='Whom was paid by the client for this invoice.', null=True, verbose_name='Invoice Paid to'),
        ),
    ]
