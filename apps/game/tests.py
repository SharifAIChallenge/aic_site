import datetime
from unittest import skip

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from apps.accounts import tests
from apps.accounts.tests import populate_challenges, populate_teams, populate_users, populate_competitions
from apps.accounts.models import Team, UserParticipatesOnTeam
from apps.game.models import Match, Challenge, Competition, Game
from apps.game.models.challenge import TeamParticipatesChallenge
from django.contrib.auth.models import User


class TestGame(TransactionTestCase):
    def setUp(self):
        super().setUp()
        populate_users()
        populate_teams()
        populate_challenges()
        populate_competitions()
        pass

        # def test_functions(self):
        #     teams = Team.objects.all()
        #     competition = Competition.objects.get(type='elim')
        #     challenge = Challenge.objects.all()[0]
        #     team_participation = []
        #     for team in teams:
        #         participation = TeamParticipatesChallenge()
        #         participation.team = team
        #         participation.challenge = challenge
        #         participation.save()
        #         team_participation.append(participation)
        #
        #     matches = []
        #     for i in range(3):
        #         matches.append(Match())
        #         participants = []
        #         for j in range(2):
        #             participant = Participant()
        #             participant.depend = team_participation[(i + j) % 3]
        #             participant.save()
        #             participants.append(participant)
        #         matches[i].part1 = participants[0]
        #         matches[i].part2 = participants[1]
        #         matches[i].competition = competition
        #         matches[i].save()
        #
        #     challenge.competitions = [competition]
        #     challenge.save()
        #
        #     ''' teams and matches initialized '''
        #
        #     self.assertTrue(upload_file(open("README.md", "r")) is not None)
        #
        #     file_token1 = upload_file(open("README.md", "r"))
        #
        #     submit_tokens1 = compile_submissions([file_token1])
        #     TeamSubmission.objects.create(team=team_participation[0], infra_token=submit_tokens1[0]["run_id"])
        #
        #     time.sleep(0.4)  # Wait for the compilation results
        #
        #     file_token2 = upload_file(open("README.md", "r"))
        #     submit_tokens2 = compile_submissions([file_token2], "AIC2018")
        #     TeamSubmission.objects.create(team=team_participation[1], infra_token=submit_tokens2[0]["run_id"])
        #
        #     time.sleep(0.4)  # Wait for the compilation results
        #
        #     match_tokens = run_matches([matches[0]])
        #     Match.objects.filter(id=matches[0].id).update(infra_token=match_tokens[0]["run_id"])
        #
        #     time.sleep(0.4)  # Wait for the matches results
        #
        #     self.assertEqual(TeamSubmission.objects.get(infra_token=submit_tokens1[0]["run_id"]).infra_compile_message, 'ok')
        #     self.assertEqual(TeamSubmission.objects.get(infra_token=submit_tokens2[0]["run_id"]).infra_compile_message, 'ok')
        #     self.assertEqual(Match.objects.get(infra_token=match_tokens[0]["run_id"]).infra_match_message, 'ok')


class TestScheduling(TestCase):
    def setUp(self):
        super().setUp()
        tests.populate_users()
        tests.populate_teams()
        tests.populate_challenges()
        tests.populate_competitions()

    @skip("Map model known issue.")
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
        # 2 -> 4
        # 1 -> 4
        # 3 -> 2
        # 1 -> 2
        # 4 -> 3
        # 3 -> 1
        # 4 -> 2
        # 4 -> 1
        # 2 -> 3
        # 2 -> 1
        # 3 -> 4

        matches = list(Match.objects.all())
        self.assertEqual(matches[0].part1.object_id, 1)
        self.assertEqual(matches[0].part2.object_id, 3)
        self.assertEqual(matches[1].part1.object_id, 2)
        self.assertEqual(matches[1].part2.object_id, 4)
        self.assertEqual(matches[2].part1.object_id, 1)
        self.assertEqual(matches[2].part2.object_id, 4)
        self.assertEqual(matches[3].part1.object_id, 3)
        self.assertEqual(matches[3].part2.object_id, 2)
        self.assertEqual(matches[4].part1.object_id, 1)
        self.assertEqual(matches[4].part2.object_id, 2)
        self.assertEqual(matches[5].part1.object_id, 4)
        self.assertEqual(matches[5].part2.object_id, 3)
        self.assertEqual(matches[6].part2.object_id, 1)
        self.assertEqual(matches[6].part1.object_id, 3)
        self.assertEqual(matches[7].part2.object_id, 2)
        self.assertEqual(matches[7].part1.object_id, 4)
        self.assertEqual(matches[8].part2.object_id, 1)
        self.assertEqual(matches[8].part1.object_id, 4)
        self.assertEqual(matches[9].part2.object_id, 3)
        self.assertEqual(matches[9].part1.object_id, 2)
        self.assertEqual(matches[10].part2.object_id, 1)
        self.assertEqual(matches[10].part1.object_id, 2)
        self.assertEqual(matches[11].part2.object_id, 4)
        self.assertEqual(matches[11].part1.object_id, 3)

    @skip("Map model known issue.")
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
        # 3 -> 4
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
        self.assertEqual(matches[1].part2.object_id, 4)
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

    @skip("Map model known issue.")
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
            # print(str(match.part1.object_id) + '->' + str(match.part2.object_id))
            pass

        # first round
        # match 1-8
        start_ind = 1
        power2 = 16
        power2 = int(power2 / 2)
        for i in range(power2):
            self.assertEqual(matches[start_ind + i - 1].part1.object_id, 2 * i + 1)
            self.assertEqual(matches[start_ind + i - 1].part2.object_id, 2 * i + 2)
        prev_third_ind = 1
        prev_start_ind = 1
        start_ind = start_ind + power2
        while power2 >= 1:
            power2 = int(power2 / 2)
            # match 9-12
            for i in range(power2):
                self.assertEqual(matches[start_ind + i - 1].part1.object_id, prev_start_ind + 2 * i)
                self.assertEqual(matches[start_ind + i - 1].part2.object_id, prev_start_ind + 2 * i + 1)
            prev_start_ind = start_ind
            start_ind = start_ind + power2
            # match 13-16
            for i in range(power2):
                self.assertEqual(matches[start_ind + i - 1].part1.object_id, prev_third_ind + 2 * i)
                self.assertEqual(matches[start_ind + i - 1].part2.object_id, prev_third_ind + 2 * i + 1)
            second_ind = start_ind
            start_ind = start_ind + power2
            # match 17-20
            for i in range(power2):
                self.assertEqual(matches[start_ind + i - 1].part1.object_id, second_ind + i)
                self.assertEqual(matches[start_ind + i - 1].part2.object_id, second_ind - i - 1)
            prev_third_ind = start_ind
            start_ind = start_ind + power2

        self.assertEqual(matches[start_ind - 1].part1.object_id, start_ind - 1)
        self.assertEqual(matches[start_ind - 1].part2.object_id, start_ind - 3)

        self.assertEqual(matches[start_ind].part1.object_id, start_ind - 1)
        self.assertEqual(matches[start_ind].part2.object_id, start_ind - 3)


class TestScoreboard(TestCase):
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
                team.name = int(i / 3 + 1)
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
        game.name = "AIC Game 2018"
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

    def render_double_elimination(request, competition_id):
        matches = list(Competition.objects.get(pk=int(competition_id)).matches.all())
        win_matches = []
        lose_matches = []
        cur_round_length = int((len(matches) + 1) / 4)  # for 16 teams there is 31 matches and cur_round_length is 8
        win_matches.append([])
        for i in range(cur_round_length):
            win_matches[len(win_matches) - 1].append(matches[i].get_match_result())

        start_round_index = cur_round_length
        cur_round_length = int(cur_round_length / 2)

        while cur_round_length >= 1:
            win_matches.append([])
            for i in range(cur_round_length):
                win_matches[len(win_matches) - 1].append(matches[start_round_index + i].get_match_result())

            lose_matches.append([])
            for i in range(cur_round_length):
                lose_matches[len(lose_matches) - 1].append(
                    matches[start_round_index + cur_round_length + i].get_match_result()
                )

            lose_matches.append([])
            for i in range(cur_round_length):
                lose_matches[len(lose_matches) - 1].append(
                    matches[start_round_index + 2 * cur_round_length + i].get_match_result()
                )
            start_round_index += 3 * cur_round_length
            cur_round_length = int(cur_round_length / 2)

        return [win_matches, lose_matches]

    @skip("Map model known issue.")
    def test_scoreboard_double_elimination(self):
        challenge = Challenge.objects.all()[0]
        for team in Team.objects.all():
            participation = TeamParticipatesChallenge()
            participation.team = team
            participation.challenge = challenge
            participation.save()

        competition = Competition(challenge=challenge, type='double')
        competition.save()
        competition.create_new_double_elimination(teams=Team.objects.all())
        list_matches = list(Match.objects.all())

        matches = self.render_double_elimination(competition.id)
        # print(matches)
        # print(len(matches))
        for wl in range(len(matches)):
            # print('win/lose = ' + str(wl))
            for r in range(len(matches[wl])):
                # print('round = ' + str(r))
                for m in range(len(matches[wl][r])):
                    # print('match = ' + str(m))
                    for i in range(len(matches[wl][r][m])):
                        # print('i = ' + str(i) + ' , ' + matches[wl][r][m][i])
                        pass

        for i in range(len(list_matches)):
            list_matches[i].done_match()

        matches = self.render_double_elimination(competition.id)
        # print(matches)
        # print(len(matches))
        for wl in range(len(matches)):
            # print('win/lose = ' + str(wl))
            for r in range(len(matches[wl])):
                # print('round = ' + str(r))
                for m in range(len(matches[wl][r])):
                    # print('match = ' + str(m))
                    for i in range(len(matches[wl][r][m])):
                        # print('i = ' + str(i) + ' , ' + matches[wl][r][m][i])
                        pass
