# Generated by Django 3.1.4 on 2021-02-05 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autotasks', '0015_auto_20210205_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='automatedtask',
            name='status',
            field=models.CharField(choices=[('passing', 'Passing'), ('failing', 'Failing'), ('pending', 'Pending')], default='pending', max_length=30),
        ),
    ]
