from django.db import models


class Poll(models.Model):
    url = models.CharField(max_length=1000, unique=True)
    question_text = models.CharField(max_length=10000)

