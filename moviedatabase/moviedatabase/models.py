from django.db import models
from django.contrib.postgres.fields import JSONField


class Movie(models.Model):
    title = models.TextField()
    details = JSONField()
