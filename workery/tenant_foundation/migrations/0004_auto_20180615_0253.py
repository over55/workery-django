# Generated by Django 2.0.5 on 2018-06-15 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0003_auto_20180615_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='hours',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, help_text='The total amount of hours worked on for this order by the associate.', max_digits=7, null=True, verbose_name='Hours'),
        ),
    ]