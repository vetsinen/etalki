# Generated by Django 2.1.4 on 2019-01-16 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingapp', '0013_auto_20190109_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='color',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
