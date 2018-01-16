# Generated by Django 2.0 on 2018-01-16 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_foundation', '0005_auto_20180114_0108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='text',
            field=models.CharField(db_index=True, help_text='The text content of this tag.', max_length=31, unique=True, verbose_name='Text'),
        ),
    ]
