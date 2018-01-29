from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=256)
    infra_token = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name