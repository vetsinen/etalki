# Generated by Django 2.1.4 on 2018-12-09 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookingapp', '0008_auto_20181207_0503'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slot2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utcstart', models.DateTimeField()),
                ('utcdate', models.CharField(blank=True, max_length=10)),
            ],
        ),
    ]