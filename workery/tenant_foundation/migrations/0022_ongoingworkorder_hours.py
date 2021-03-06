# Generated by Django 2.0.7 on 2018-08-31 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0021_ongoingworkorder_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='ongoingworkorder',
            name='hours',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, help_text='The total amount of hours worked on for this ongoing order by the associate.', max_digits=7, null=True, verbose_name='Hours'),
        ),
    ]
