# Generated by Django 2.1.4 on 2018-12-04 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='hours',
            field=models.IntegerField(default=0),
        ),
    ]
