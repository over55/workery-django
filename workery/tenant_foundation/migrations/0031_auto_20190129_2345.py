# Generated by Django 2.0.9 on 2019-01-29 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0030_auto_20190129_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='deactivation_reason',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2, 'Blacklisted'), (3, 'Moved'), (4, 'Deceased'), (5, 'Do not contact'), (0, 'Not specified'), (1, 'Other')], default=0, help_text='The reason why this customer was deactivated.', verbose_name='Deactivation reason'),
        ),
    ]
