# Generated by Django 2.1.4 on 2018-12-05 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=10)),
                ('periods', models.DateField()),
            ],
        ),
    ]