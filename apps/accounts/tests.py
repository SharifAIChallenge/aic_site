import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from apps.accounts.models import Team, UserParticipatesOnTeam
from apps.game.models import Challenge, Competition, Match, Game, Participant
from apps.game.models.challenge import TeamParticipatesChallenge


def populate_users():
    for i in range(9):
        user = User()
        user.username = str(i) + "DummyCamelCaseTeamForTest"
        user.save()


def populate_teams():
    users = User.objects.all()
    i = 0
    team = None
    for user in users:
        if i % 3 == 0:
            team = Team()
            team.name = i / 3 + 1
            team.save()
        participation = UserParticipatesOnTeam()
        participation.user = user
        participation.team = team
        participation.save()
        i += 1


def populate_challenges():
    challenge = Challenge()
    challenge.title = "Dummiest Challenge created ever"
    challenge.start_time = timezone.now()
    challenge.end_time = timezone.now() + datetime.timedelta(days=1)
    challenge.registration_start_time = challenge.start_time
    challenge.registration_end_time = challenge.end_time
    challenge.registration_open = True
    challenge.team_size = 3
    challenge.entrance_price = 1000
    game = Game()
    game.name = "AIC 2018"
    game.save()
    challenge.game = game
    challenge.save()


def populate_competitions():
    challenge = Challenge.objects.all()[0]
    types = ['elim', 'league', 'double']
    for i in range(3):
        competition = Competition()
        competition.type = types[i]
        competition.challenge = challenge
        competition.save()