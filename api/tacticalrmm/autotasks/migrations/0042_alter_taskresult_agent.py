# Generated by Django 4.2.9 on 2024-02-09 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0058_alter_agent_time_zone'),
        ('autotasks', '0041_automatedtask_crontab_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskresult',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='taskresults', to='agents.agent'),
        ),
    ]
