# Generated by Django 4.1.3 on 2023-01-23 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_integration_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration',
            name='frontend_module_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
