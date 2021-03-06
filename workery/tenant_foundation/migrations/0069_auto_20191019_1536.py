# Generated by Django 2.0.13 on 2019-10-19 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0068_auto_20191018_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorderdeposit',
            name='paid_for',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Labour'), (2, 'Materials'), (3, 'Waste Removal'), (4, 'Amount Due')], help_text='What was this deposit for?', verbose_name='Paid for'),
        ),
    ]
