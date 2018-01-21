import time

import datetime
from django.test import TestCase, TransactionTestCase

from apps.accounts import tests
from apps.accounts.models import Team
from apps.game.models import Challenge, Competition, TeamParticipatesChallenge, Match
# Create your tests here.
from django.utils import timezone
from django.contrib.auth.models import User

from apps.accounts.models import Team, UserParticipatesOnTeam
from apps.accounts.tests import populate_users, populate_teams, populate_challenges, populate_competitions
from apps.game.functions import upload_file, compile_submissions, run_matches
from apps.game.models import Match, TeamSubmission, Challenge, Game, Competition, Participant
from apps.game.models.challenge import TeamParticipatesChallenge


class TestGame(TransactionTestCase):

    def setUp(self):
        super().setUp()
        populate_users()
        populate_teams()
        populate_challenges()
        populate_competitions()
        pass

    def test_functions(self):
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

        ''' teams and matches initialized '''

        # self.assertTrue(upload_file('') is not None)
        #
        # file_token1 = upload_file('')
        # submit_tokens1 = compile_submissions([file_token1], "AIC2018")
        # TeamSubmission.objects.create(team=team_participation[0], infra_token=submit_tokens1[0]["token"])
        #
        # time.sleep(0.4)  # Wait for the compilation results
        #
        # file_token2 = upload_file('')
        # submit_tokens2 = compile_submissions([file_token2], "AIC2018")
        # TeamSubmission.objects.create(team=team_participation[1], infra_token=submit_tokens2[0]["token"])
        #
        # time.sleep(0.4)  # Wait for the compilation results
        #
        # match_tokens = run_matches([matches[0]])
        # Match.objects.filter(id=matches[0].id).update(infra_token=match_tokens[0]["token"])
        #
        # time.sleep(0.4)  # Wait for the matches results
        #
        # self.assertEqual(TeamSubmission.objects.get(infra_token=submit_tokens1[0]["token"]).infra_compile_message, 'ok')
        # self.assertEqual(TeamSubmission.objects.get(infra_token=submit_tokens2[0]["token"]).infra_compile_message, 'ok')
        # self.assertEqual(Match.objects.get(infra_token=match_tokens[0]["token"]).infra_match_message, 'ok')



class TestScheduling(TestCase):
    def setUp(self):
        super().setUp()
        tests.populate_users()
        tests.populate_teams()
        tests.populate_challenges()
        tests.populate_competitions()

    def test_create_new_league(self):
        challenge = Challenge.objects.all()[0]
        for team in Team.objects.all():
            participation = TeamParticipatesChallenge()
            participation.team = team
            participation.challenge = challenge
            participation.save()
        competition = Competition(challenge=challenge, type='league')
        competition.save()
        competition.create_new_league(teams=Team.objects.all())

        # expected result
        # 1 -> 3
        # 2 -> None
        # 1 -> None
        # 3 -> 2
        # 1 -> 2
        # None -> 3
        # 3 -> 1
        # None -> 2
        # None -> 1
        # 2 -> 3
        # 2 -> 1
        # 3 -> None

        matches = list(Match.objects.all())
        self.assertEqual(matches[0].part1.object_id, 1)
        self.assertEqual(matches[0].part2.object_id, 3)
        self.assertEqual(matches[1].part1.object_id, 2)
        self.assertEqual(matches[1].part2.object_id, None)
        self.assertEqual(matches[2].part1.object_id, 1)
        self.assertEqual(matches[2].part2.object_id, None)
        self.assertEqual(matches[3].part1.object_id, 3)
        self.assertEqual(matches[3].part2.object_id, 2)
        self.assertEqual(matches[4].part1.object_id, 1)
        self.assertEqual(matches[4].part2.object_id, 2)
        self.assertEqual(matches[5].part1.object_id, None)
        self.assertEqual(matches[5].part2.object_id, 3)
        self.assertEqual(matches[6].part2.object_id, 1)
        self.assertEqual(matches[6].part1.object_id, 3)
        self.assertEqual(matches[7].part2.object_id, 2)
        self.assertEqual(matches[7].part1.object_id, None)
        self.assertEqual(matches[8].part2.object_id, 1)
        self.assertEqual(matches[8].part1.object_id, None)
        self.assertEqual(matches[9].part2.object_id, 3)
        self.assertEqual(matches[9].part1.object_id, 2)
        self.assertEqual(matches[10].part2.object_id, 1)
        self.assertEqual(matches[10].part1.object_id, 2)
        self.assertEqual(matches[11].part2.object_id, None)
        self.assertEqual(matches[11].part1.object_id, 3)

    def test_create_new_double_elimination(self):
        challenge = Challenge.objects.all()[0]
        for team in Team.objects.all():
            participation = TeamParticipatesChallenge()
            participation.team = team
            participation.challenge = challenge
            participation.save()

        competition = Competition(challenge=challenge, type='double')
        competition.save()
        competition.create_new_double_elimination(teams=Team.objects.all())

        # expected result
        # 1 -> 2
        # 3 -> None
        # 1 -> 2
        # 1 -> 2
        # 4 -> 3
        # 5 -> 3
        # 5 -> 3
        #
        matches = list(Match.objects.all())
        self.assertEqual(matches[0].part1.object_id, 1)
        self.assertEqual(matches[0].part2.object_id, 2)
        self.assertEqual(matches[1].part1.object_id, 3)
        self.assertEqual(matches[1].part2.object_id, None)
        self.assertEqual(matches[2].part1.object_id, 1)
        self.assertEqual(matches[2].part2.object_id, 2)
        self.assertEqual(matches[3].part1.object_id, 1)
        self.assertEqual(matches[3].part2.object_id, 2)
        self.assertEqual(matches[4].part1.object_id, 4)
        self.assertEqual(matches[4].part2.object_id, 3)
        self.assertEqual(matches[5].part1.object_id, 5)
        self.assertEqual(matches[5].part2.object_id, 3)
        self.assertEqual(matches[6].part1.object_id, 5)
        self.assertEqual(matches[6].part2.object_id, 3)

class TestDoubleElimination(TestCase):

    def populate_users(self):
        for i in range(48):
            user = User()
            user.username = str(i) + "DummyCamelCaseTeamForTest"
            user.save()

    def populate_teams(self):
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

    def populate_challenges(self):
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

    def populate_competitions(self):
        challenge = Challenge.objects.all()[0]
        types = ['elim', 'league', 'double']
        for i in range(3):
            competition = Competition()
            competition.type = types[i]
            competition.challenge = challenge
            competition.save()

    def setUp(self):
        super().setUp()
        self.populate_users()
        self.populate_teams()
        self.populate_challenges()
        self.populate_competitions()

    def test_create_new_double_elimination(self):
        challenge = Challenge.objects.all()[0]
        for team in Team.objects.all():
            participation = TeamParticipatesChallenge()
            participation.team = team
            participation.challenge = challenge
            participation.save()

        competition = Competition(challenge=challenge, type='double')
        competition.save()
        competition.create_new_double_elimination(teams=Team.objects.all())

        # expected result
        # 1->2
        # 3->4
        # 5->6
        # 7->8
        # 9->10
        # 11->12
        # 13->14
        # 15->16
        # 1->2
        # 3->4
        # 5->6
        # 7->8
        # 1->2
        # 3->4
        # 5->6
        # 7->8
        # 13->12
        # 14->11
        # 15->10
        # 16->9
        # 9->10
        # 11->12
        # 17->18
        # 19->20
        # 23->22
        # 24->21
        # 21->22
        # 25->26
        # 28->27
        # 29->27
        # 29->27
        #
        matches = list(Match.objects.all())
        for match in matches:
            print(str(match.part1.object_id) + '->' + str(match.part2.object_id))

        # first round
        # match 1-8
        start_ind = 1
        power2 = 16
        power2 = int(power2/2)
        for i in range(power2):
            self.assertEqual(matches[start_ind + i - 1].part1.object_id, 2*i+1)
            self.assertEqual(matches[start_ind + i - 1].part2.object_id, 2*i+2)
        prev_third_ind = 1
        prev_start_ind = 1
        start_ind = start_ind + power2
        while power2>=1:
            power2 = int(power2/2)
            # match 9-12
            for i in range(power2):
                self.assertEqual(matches[start_ind + i - 1].part1.object_id, prev_start_ind + 2 * i)
                self.assertEqual(matches[start_ind + i - 1].part2.object_id, prev_start_ind + 2 * i + 1)
            prev_start_ind = start_ind
            start_ind = start_ind + power2
            #match 13-16
            for i in range(power2):
                self.assertEqual(matches[start_ind + i - 1].part1.object_id, prev_third_ind + 2 * i)
                self.assertEqual(matches[start_ind + i - 1].part2.object_id, prev_third_ind + 2 * i + 1)
            second_ind = start_ind
            start_ind = start_ind + power2
            #match 17-20
            for i in range(power2):
                self.assertEqual(matches[start_ind + i - 1].part1.object_id, second_ind + i)
                self.assertEqual(matches[start_ind + i - 1].part2.object_id, second_ind - i - 1)
            prev_third_ind = start_ind
            start_ind = start_ind + power2

        self.assertEqual(matches[start_ind - 1].part1.object_id, start_ind - 1)
        self.assertEqual(matches[start_ind - 1].part2.object_id, start_ind - 3)

        self.assertEqual(matches[start_ind].part1.object_id, start_ind - 1)
        self.assertEqual(matches[start_ind].part2.object_id, start_ind - 3)


