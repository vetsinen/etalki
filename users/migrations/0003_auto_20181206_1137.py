# Generated by Django 2.1.4 on 2018-12-06 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='city',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='customuser',
            name='timezone',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
