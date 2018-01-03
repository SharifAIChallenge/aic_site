from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)
    infra_token = models.CharField(max_length=255, unique=True)

