from django.db import models

# Create your models here.

class URLShortner(models.Model):
    main = models.URLField()
    shortened = models.CharField(max_length=100, unique=True)