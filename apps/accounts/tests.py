import datetime
import io
import json
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TransactionTestCase, Client
from django.utils import timezone

from apps.accounts.models import Team, UserParticipatesOnTeam
from apps.game import functions
from apps.game.models import Challenge, Competition, Match, Game, Participant, TeamSubmission, Map
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


def populate_maps():
    for i in range(3):
        map = Map()
        map.name = 'map ' + str(i)
        map.save()


def populate_competitions():
    challenge = Challenge.objects.all()[0]
    maps = list(Map.objects.all())
    types = ['elim', 'league', 'double']
    for i in range(3):
        competition = Competition()
        competition.type = types[i]
        competition.challenge = challenge
        competition.save()
        for map in maps:
            competition.maps.add(map)


class TestTeam(TransactionTestCase):
    def setUp(self):
        super().setUp()
        populate_users()
        populate_teams()
        populate_challenges()
        populate_maps()
        populate_competitions()

    def test_get_team_matches(self):
        teams = Team.objects.all()
        competition = Competition.objects.get(type='elim')
        challenge = Challenge.objects.all()[0]
        team_participation = []
        for team in teams:
            participation = TeamParticipatesChallenge()
            participation.team = team
            participation.challenge = challenge
            participation.save()
            team_participation.append(participation)

        matches = []
        for i in range(3):
            matches.append(Match())
            participants = []
            for j in range(2):
                participant = Participant()
                participant.depend = team_participation[(i + j) % 3]
                participant.save()
                participants.append(participant)
            matches[i].part1 = participants[0]
            matches[i].part2 = participants[1]
            matches[i].competition = competition
            matches[i].save()

        challenge.competitions = [competition]
        challenge.save()

        team0_matches = teams[0].get_competition_matches(competition.id)

        self.assertEqual(len(team0_matches), 2)

    def test_panel(self):
        # prepare data
        teams = Team.objects.all()
        challenge = Challenge.objects.all()[0]
        team_participation = []
        for team in teams:
            participation = TeamParticipatesChallenge()
            participation.team = team
            participation.challenge = challenge
            participation.save()
            team_participation.append(participation)

        # test login required
        client = Client()
        response = client.get('/accounts/panel/')
        self.assertEqual(response.status_code, 302)
        # test that it says OK
        client.force_login(User.objects.all()[0])
        response = client.get('/accounts/panel/')
        self.assertEqual(response.status_code, 302)
        participation = TeamParticipatesChallenge.objects.all()[0]
        response = client.post(
            '/accounts/panel/' + str(participation.id),
            {
                'file': io.StringIO("Log the game"),
                'team': participation.id,
                'language': 'cpp'
            }
        )
        self.assertEqual(response.status_code, 200)
        # test that it functions
        time.sleep(0.4)
        self.assertEqual(TeamSubmission.objects.filter(language="cpp").count(), 1)
        response = client.post(
            '/accounts/panel/' + str(participation.id),
            {
                'file': io.StringIO("Log the game"),
                'team': participation.id,
                'language': 'cpp'
            }
        )
        self.assertEqual(response.status_code, 200)
        time.sleep(0.4)
        self.assertEqual(TeamSubmission.objects.filter(language="cpp").count(), 2)
        submissions = list(TeamSubmission.objects.all())
        self.assertFalse(submissions[0].is_final)
        self.assertTrue(submissions[1].is_final)

        # successful scenario coverage
        self.assertEqual(submissions[0].status, 'compiling')

        json_str = json.dumps({
            'id': submissions[0].infra_compile_token,
            'operation': 'compile',
            'status': 2,
            'parameters': {
                'code_compiled_zip': functions.random_token(),
                'code_log': functions.random_token()
            }
        })
        response = client.post('/game/api/report', data=json_str, content_type='application/json',
                               **{'HTTP_AUTHORIZATION': settings.INFRA_AUTH_TOKEN})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TeamSubmission.objects.all().first().status, 'compiled')
