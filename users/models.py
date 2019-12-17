from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    city = models.CharField(max_length=30, blank=True)
    hours = models.IntegerField(default=0)
    lastteacher = models.CharField(max_length=30, blank=True)
    # https://stackoverflow.com/questions/9454212/save-time-zone-in-django-models
    timezone = models.CharField(max_length=100, blank=True, null=True, ), #choices=TIMEZONES
    timeoffset = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.email