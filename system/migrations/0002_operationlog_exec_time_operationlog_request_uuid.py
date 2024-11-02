# Generated by Django 5.1.2 on 2024-10-20 08:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='operationlog',
            name='exec_time',
            field=models.FloatField(blank=True, null=True, verbose_name='Execution time'),
        ),
        migrations.AddField(
            model_name='operationlog',
            name='request_uuid',
            field=models.UUIDField(blank=True, null=True, verbose_name='Request ID'),
        ),
    ]