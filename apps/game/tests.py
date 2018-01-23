import time
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

        self.assertTrue(upload_file('') is not None)

        file_token1 = upload_file('')
        submit_tokens1 = compile_submissions([file_token1], "AIC2018")
        TeamSubmission.objects.create(team=team_participation[0], infra_token=submit_tokens1[0]["token"])

        time.sleep(0.4)  # Wait for the compilation results

        file_token2 = upload_file('')
        submit_tokens2 = compile_submissions([file_token2], "AIC2018")
        TeamSubmission.objects.create(team=team_participation[1], infra_token=submit_tokens2[0]["token"])

        time.sleep(0.4)  # Wait for the compilation results

        match_tokens = run_matches([matches[0]])
        Match.objects.filter(id=matches[0].id).update(infra_token=match_tokens[0]["token"])

        time.sleep(0.4)  # Wait for the matches results

        self.assertEqual(TeamSubmission.objects.get(infra_token=submit_tokens1[0]["token"]).infra_compile_message, 'ok')
        self.assertEqual(TeamSubmission.objects.get(infra_token=submit_tokens2[0]["token"]).infra_compile_message, 'ok')
        self.assertEqual(Match.objects.get(infra_token=match_tokens[0]["token"]).infra_match_message, 'ok')



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
