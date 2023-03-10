# Generated by Django 4.1.3 on 2023-01-21 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_alter_coresettings_default_time_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('desc', models.CharField(blank=True, max_length=100, null=True)),
                ('version', models.CharField(blank=True, max_length=20, null=True)),
                ('latest_version', models.CharField(blank=True, max_length=20, null=True)),
                ('installed', models.BooleanField(default=False)),
                ('installed_on', models.DateTimeField(blank=True, null=True)),
                ('update_available', models.BooleanField(default=False)),
                ('install_url', models.CharField(max_length=255)),
            ],
        ),
    ]
