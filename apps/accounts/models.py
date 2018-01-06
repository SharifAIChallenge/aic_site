from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    phone_number = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Team(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class UserParticipatesOnTeam(models.Model):
    team = models.ForeignKey(Team, related_name='participants')
    user = models.ForeignKey(User, related_name='teams')
