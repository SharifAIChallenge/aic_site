from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    phone_number = models.CharField(max_length=11, null=True, blank=True)


class Team(models.Model):
    name = models.CharField(max_length=255)


class UserParticipatesOnTeam(models.Model):
    team = models.ForeignKey(Team, related_name='participants')
    user = models.ForeignKey(User, related_name='teams')

