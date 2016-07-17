from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Session(models.Model):

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    def __str__(self):
        return str(self.first_name + ' ' + self.last_name)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    fbid = models.CharField(max_length=20)

    session_id = models.CharField(max_length=60, primary_key=True)

    wit_context = JSONField(default={})
