# Generated by Django 2.1.4 on 2018-12-06 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingapp', '0005_auto_20181205_1159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='minute',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='start',
        ),
        migrations.AddField(
            model_name='lesson',
            name='author',
            field=models.CharField(default='admin', max_length=30),
        ),
        migrations.AddField(
            model_name='lesson',
            name='date',
            field=models.DateField(default='2018-12-06'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='teacher',
            field=models.CharField(default='bill', max_length=20),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='hour',
            field=models.IntegerField(default=10, max_length=2),
        ),
    ]
