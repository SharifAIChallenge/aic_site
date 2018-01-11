from django.test import TestCase

from apps.accounts import tests
from apps.accounts.models import Team
from apps.game.models import Challenge, Competition


class TestScheduling(TestCase):
    def setUp(self):
        super().setUp()
        tests.populate_users()
        tests.populate_teams()
        tests.populate_challenges()
        tests.populate_competitions()

    def test_create_new_league(self):
        competition = Competition(teams=Team.objects.all(), challenge=Challenge.objects.all()[0], type= 'league')
        competition.save()
        pass
