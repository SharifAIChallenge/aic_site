from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=256)
    infra_token = models.CharField(max_length=256, unique=True)


    def __str__(self):
        if self.name is None:
            return str(self.id)
        else:
            return self.name