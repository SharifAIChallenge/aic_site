from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=128, default="")
    team = models.CharField(max_length=20, default="")
    image = models.ImageField(null=True, upload_to='staff_pic')

    @property
    def color(self):
        if self.team == 'executive':
            return 'red'
        elif self.team == 'site' or self.team == 'graphic' or self.team == 'infrastructure' or self.team == 'server and client':
            return 'blue'
        else:
            return 'orange'

# Create your models here.
