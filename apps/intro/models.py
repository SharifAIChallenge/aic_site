from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=128, default="")
    team = models.CharField(max_length=20, default="")
    image = models.ImageField(null=True, upload_to='staff_pic')
# Create your models here.
