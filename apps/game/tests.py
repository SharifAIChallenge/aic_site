from django.test import TestCase

from apps.accounts import tests
from apps.accounts.models import Team
from apps.game.models import Challenge, Competition, TeamParticipatesChallenge, Match


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
        # 5 -> 4
        # 5 -> 4
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
        self.assertEqual(matches[5].part2.object_id, 4)
        self.assertEqual(matches[6].part1.object_id, 5)
        self.assertEqual(matches[6].part2.object_id, 4)