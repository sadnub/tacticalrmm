# Generated by Django 4.2.9 on 2024-02-09 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_remove_role_can_ping_agents'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='can_manage_servertasks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='role',
            name='can_run_servertasks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='role',
            name='can_view_servertasks',
            field=models.BooleanField(default=False),
        ),
    ]
