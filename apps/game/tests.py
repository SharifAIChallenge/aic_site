import time
from django.test import TestCase, TransactionTestCase

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

