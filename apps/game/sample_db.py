from apps.game.models import *
import datetime

from django.utils import timezone

from apps.accounts.models import Team, UserParticipatesOnTeam
from django.contrib.auth.models import User


def create_sample_db():
    populate_users(24)
    populate_teams()
    populate_games()
    populate_challenges()
    populate_maps()
    populate_competitions()

def populate_users(num):
    for i in range(num):
        user = User()
        user.username = str(i) + " test_user"
        user.save()


def populate_teams():
    users = User.objects.all()

    cnt = 0
    team = None
    for user in users:
        if cnt % 3 == 0:
            team = Team()
            team.name = int(cnt / 3 + 1)
            team.save()
        participation = UserParticipatesOnTeam()
        participation.user = user
        participation.team = team
        participation.save()
        cnt += 1

def populate_games():
    token = str(len(Game.objects.all()))
    game = Game(name='swarm', infra_token=token)
    game.save()


def populate_challenges():

    # challenge = Challenge()
    # challenge.title = "bye challenge for logic, don't create competition in this challenge"
    # challenge.start_time = timezone.now()
    # challenge.end_time = timezone.now() + datetime.timedelta(days=1)
    # challenge.registration_start_time = challenge.start_time
    # challenge.registration_end_time = challenge.end_time
    # challenge.registration_open = False
    # challenge.team_size = 0
    # challenge.entrance_price = 0
    # challenge.game = Game.objects.all()[0]
    # challenge.save()
    #
    # participation = TeamParticipatesChallenge()
    # participation.team = Team.objects.all()[0]
    # participation.challenge = challenge
    # participation.save()

    ###

    challenge = Challenge()
    challenge.title = "Dummiest Challenge created ever"
    challenge.start_time = timezone.now()
    challenge.end_time = timezone.now() + datetime.timedelta(days=1)
    challenge.registration_start_time = challenge.start_time
    challenge.registration_end_time = challenge.end_time
    challenge.registration_open = True
    challenge.team_size = 3
    challenge.entrance_price = 1000
    challenge.game = Game.objects.all()[0]
    challenge.save()

    for team in Team.objects.all():
        # if team == Team.objects.all()[0]:
        #     continue
        participation = TeamParticipatesChallenge()
        participation.team = team
        participation.challenge = challenge
        participation.save()

def populate_maps():
    for i in range(3):
        map = Map()
        map.name = 'map ' + str(i)
        map.save()

def populate_competitions():
    challenge = Challenge.objects.all()[0]
    maps = list(Map.objects.all())
    types = ['league', 'double']
    # team_size = [2, 4, 8, 16, 32, 3, 5, 6, 7, 15]
    team_size = [4, 8]
    for k in range(2):
        for i in range(len(team_size)):
            competition = Competition()
            competition.type = types[k]
            competition.challenge = challenge
            competition.save()

            for map in maps:
                competition.maps.add(map)

            if k == 0:
                competition.create_new_league(teams=Team.objects.all()[0: (team_size[i])], rounds_num=1)

            if k == 1:
                competition.create_new_double_elimination(teams=Team.objects.all()[0: (team_size[i])])

            # matches = list(competition.matches.all())
            # for match in matches:
            #     match.done_match()

    competition = Competition()
    competition.type = 'friendly'
    competition.challenge = challenge
    competition.save()
    for map in maps:
        competition.maps.add(map)

    print('friendly_matches start')
    # competition.create_new_league(teams=Team.objects.all(),rounds_num=1)
    teams_size = min(len(TeamParticipatesChallenge.objects.all()), 8)
    challenge_teams = list(TeamParticipatesChallenge.objects.all()[0: teams_size])

    for i in range(teams_size):
        for j in range(teams_size):
            print(i)
            print(j)
            print(':::')
            if i < j:
                new_match = Match.objects.create(
                    competition=competition,
                    part1=Participant.objects.create(
                        depend=challenge_teams[i],
                        depend_method='itself'
                    ),
                    part2=Participant.objects.create(
                        depend=challenge_teams[j],
                        depend_method='itself'
                    )
                )
                for map in competition.maps.all():
                    SingleMatch.objects.create(match=new_match, map=map)
                    # print(map.name)
                new_match.done_match()
