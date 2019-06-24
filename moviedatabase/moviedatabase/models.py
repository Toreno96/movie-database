from django.db import models
from django.contrib.postgres.fields import JSONField


class Movie(models.Model):
    title = models.TextField()
    details = JSONField()


class Comment(models.Model):
    movie_id = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    added = models.DateTimeField(auto_now_add=True)
