from django.db import models

class Notification(models.Model):
    email = models.EmailField(null=True, unique=True)

    def __str__(self):
        return str(self.email)

class Staff(models.Model):
    name = models.CharField(max_length=20, default="")
    team = models.CharField(max_length=20, default="")
    image = models.ImageField(null=True, upload_to='staff_pic')

    def __str__(self):
        return str(self.name)

    @property
    def color(self):
        if self.team == 'executive':
            return 'red'
        elif self.team == 'Site' or self.team == 'Graphic' or self.team == 'Infrastructure' or self.team == 'Server and Client':
            return 'blue'
        else:
            return 'orange'

# Create your models here.
