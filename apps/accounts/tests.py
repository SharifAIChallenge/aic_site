from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from apps.accounts.models import Team
from apps.game.models import Challenge, Competition, Match


def populate_users():
    for i in range(9):
        user = User()
        user.username = str(i) + "DummyCamelCaseTeamForTest"
        user.save()


def populate_teams():
    users = User.objects.all()
    team_users = []
    for i in range(len(users)):
        team_users += users[i]
        if len(team_users) == 3:
            team = Team()
            team.name = i / 3 + 1
            team.participants = team_users
            team.save()
            team_users = []


def populate_challenges():
    challenge = Challenge()
    challenge.title = "Dummiest Challenge created ever"
    challenge.save()


def populate_competitions():
    challenge = Challenge.objects.all()[0]
    types = ['elim', 'league', 'double']
    for i in range(3):
        competition = Competition()
        competition.type = types[i]
        competition.challenge = challenge
        competition.save()


class TestTeam(TestCase):
    def setUp(self):
        super().setUp()
        populate_users()
        populate_teams()
        populate_challenges()
        populate_competitions()

    def test_get_team_matches(self):
        teams = Team.objects.all()
        competition = Competition.objects.get(type='elim')
        challenge = Challenge.objects.all()[0]
        for team in teams:
            team.challanges = [challenge]
            team.save()

        match1 = Match()
        match2 = Match()
        match3 = Match()

        matches = [match1, match2, match3]

        match1.part1.content_type = ContentType.objects.get_for_model(Team)
        match1.part2.content_type = ContentType.objects.get_for_model(Team)
        match2.part1.content_type = ContentType.objects.get_for_model(Team)
        match2.part2.content_type = ContentType.objects.get_for_model(Team)
        match3.part1.content_type = ContentType.objects.get_for_model(Team)
        match3.part2.content_type = ContentType.objects.get_for_model(Team)

        match1.part1.object_id = teams[0].id
        match1.part2.object_id = teams[1].id
        match2.part1.object_id = teams[0].id
        match2.part2.object_id = teams[2].id
        match3.part1.object_id = teams[1].id
        match3.part2.object_id = teams[2].id

        competition.match_set = [match1, match2, match3]

        challenge.competitions = [competition]

        for match in matches:
            match.save()

        team0_matches = teams[0].get_competition_matches(competition.id)

        self.assertEqual(len(team0_matches), 2)
