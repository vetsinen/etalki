# Generated by Django 2.1.4 on 2018-12-05 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookingapp', '0003_auto_20181205_0826'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Slots',
            new_name='Slot',
        ),
    ]
