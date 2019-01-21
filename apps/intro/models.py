from django.db import models

class Notification(models.Model):
    email = models.EmailField(null=True, unique=True)

    def __str__(self):
        return str(self.email)

# Create your models here.
