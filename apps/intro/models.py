from django.db import models

class Notification(models.Model):
    email = models.EmailField(null=True)
# Create your models here.
