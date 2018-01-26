import json
from operator import itemgetter

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse, Http404

# Create your views here.
from django.shortcuts import render

from apps.game.models import Competition, TeamParticipatesChallenge

def render_scoreboard(request, competition_id):
    competition = Competition.objects.get(pk=int(competition_id))
    if competition is None:
        # error handling in template #
        return ValueError('There is not such Competition')

    if competition.type == 'double':
        return render_double_elimination(request, competition_id)
    elif competition.type == 'league':
        return render_league(request, competition_id)


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

    #return [win_matches, lose_matches]
    return render(request, 'scoreboard/bracket.html', {'win_matches': win_matches,
                                                       'lose_matches': lose_matches})



def render_league(request, competition_id):
    matches = list(Competition.objects.get(pk=int(competition_id)).matches.all())
    league_teams = []
    league_scoreboard = []
    league_matches = []
    league_size = 0
    cnt = 0
    # print(len(matches))
    # print(matches)
    while True:
        tmp_league_size = league_size
        if matches[cnt].part1.object_id is not None:
            team1 = TeamParticipatesChallenge.objects.filter(
                challenge=Competition.objects.get(pk=int(competition_id)).challenge,
                pk=matches[cnt].part1.object_id
            )[0]
            if team1 not in league_teams:
                # print(team1.id)
                league_teams.append(team1)
                league_scoreboard.append([team1, '?', 0, 0])
                league_size += 1
        if matches[cnt].part2.object_id is not None:
            team2 = TeamParticipatesChallenge.objects.filter(
                challenge=Competition.objects.get(pk=int(competition_id)).challenge,
                pk=matches[cnt].part2.object_id
            )[0]
            if team2 not in league_teams:
                # print(team2.id)
                league_teams.append(team2)
                league_scoreboard.append([team2, '?', 0, 0])
                league_size += 1
        cnt += 1
        if tmp_league_size == league_size:
            break

    num_matches_per_week = 0
    num_weeks = 0
    if league_size % 2 == 0:
        num_matches_per_week = int(league_size / 2)
        num_weeks = league_size - 1
    else:
        num_matches_per_week = int((league_size + 1) / 2)
        num_weeks = league_size

    num_one_round_matches = num_matches_per_week * num_weeks
    num_rounds = int(len(matches) / num_one_round_matches)

    cnt = -1
    for round in range(num_rounds):
        league_matches.append([])
        for week in range(num_weeks):
            r = len(league_matches) - 1
            league_matches[r].append([])
            for i in range(num_matches_per_week):
                cnt += 1
                match_result = matches[cnt].get_match_result()
                team1 = None
                team2 = None
                if matches[cnt].part1.object_id is not None and matches[cnt].part2.object_id is not None:
                    r = len(league_matches) - 1
                    w = len(league_matches[r]) - 1
                    league_matches[r][w].append(match_result)

                if matches[cnt].part1.object_id is not None:
                    team1 = TeamParticipatesChallenge.objects.filter(
                        challenge=Competition.objects.get(pk=int(competition_id)).challenge,
                        pk=matches[cnt].part1.object_id
                    )[0]
                if matches[cnt].part2.object_id is not None:
                    team2 = TeamParticipatesChallenge.objects.filter(
                        challenge=Competition.objects.get(pk=int(competition_id)).challenge,
                        pk=matches[cnt].part2.object_id
                    )[0]
                if team1 is not None and team2 is not None:
                    for j in range(len(league_scoreboard)):
                        if league_scoreboard[j][0] == team1:
                            league_scoreboard[j][1] = match_result[0]
                            if match_result[2] != -1:
                                league_scoreboard[j][2] += match_result[2]
                            if match_result[2] > match_result[3]:
                                league_scoreboard[j][3] += 1
                        if league_scoreboard[j][0] == team2:
                            league_scoreboard[j][1] = match_result[1]
                            if match_result[3] != -1:
                                league_scoreboard[j][2] += match_result[3]
                            if match_result[3] > match_result[2]:
                                league_scoreboard[j][3] += 1

    league_scoreboard = sorted(league_scoreboard, key=itemgetter(2, 3, 1))
    #return [league_scoreboard, league_matches]

    return render(request, 'scoreboard/group_table.html', {'league_scoreboard': league_scoreboard,
                                                       'league_matches': league_matches})



from apps.game.models import TeamSubmission
from apps.game import functions


def report(request):
    if not request.content_type == 'application/json':
        return HttpResponseBadRequest()
    if request.method != 'POST':
        return HttpResponseBadRequest()

    received_json_data = json.loads(request.body.decode("utf-8"))

    if request.META.get('HTTP_AUTHORIZATION') != settings.INFRA_AUTH_TOKEN:
        return HttpResponseBadRequest()

    client, schema = functions.create_infra_client()

    reports = received_json_data

    for single_report in reports:
        if single_report['operation'] == 'compile':
            if len(TeamSubmission.objects.filter(infra_token=single_report['id'])) == 0:
                continue
            submit = TeamSubmission.objects.get(infra_token=single_report['id'])
            if single_report['status'] == 2:
                submit.infra_compile_token = single_report['parameters']['code_compiled_zip']
                if submit.status == 'compiling':
                    try:
                        logfile = functions.download_file(single_report['parameters']['code_log'])
                    except Exception as exception:
                        continue
                    log = json.load(logfile)
                    if len(log["errors"]) == 0:
                        submit.status = 'compiled'
                    else:
                        submit.status = 'failed'
                        submit.infra_compile_message = '\n'.join(error for error in log["errors"])
            elif single_report['status'] == 3:
                submit.status = 'failed'
                submit.infra_compile_message = 'Unknown error occurred maybe compilation timed out'
            submit.save()
            return JsonResponse({'success': True})
        elif single_report['operation'] == 'execute':
            # try:
            #     game = Game.objects.get(run_id=single_report['id'])
            # except Exception as exception:
            #     continue
            # print("Game is {} with status".format(game.run_id, single_report['status']))
            # if single_report['status'] == 2:
            #     logfile = client.action(schema, ['storage', 'get_file', 'read'],
            #                             params={'token': single_report['parameters']['game_log']})
            #     if logfile is None:
            #         continue
            #
            #     submissions = list(GameTeamSubmit.objects.all().filter(game=game).order_by('pk'))
            #     submissions[0].score, submissions[1].score = json.load(
            #         client.action(schema, ['storage', 'get_file', 'read'],
            #                       params={'token': single_report['parameters']['game_score']}))
            #     submissions[0].save()
            #     submissions[1].save()
            #     game.log = logfile.read()
            #     game.log_file.save(single_report['parameters']['game_log'], ContentFile(game.log))
            #     game.status = 3
            # elif single_report['status'] == 3:
            #     game.status = 4
            #     pass
            #     # run_game.delay(game.id)
            # game.save()
            return Http404()
            pass
        return HttpResponseServerError()
