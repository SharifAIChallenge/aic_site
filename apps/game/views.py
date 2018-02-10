import codecs
import json
import logging
from operator import itemgetter

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from apps.game import functions
from apps.game.models import Competition, TeamParticipatesChallenge, TeamSubmission, SingleMatch

logger = logging.getLogger(__name__)


@login_required()
def render_scoreboard(request, competition_id):
    competition = Competition.objects.get(pk=int(competition_id))
    if competition is None:
        # error handling in template #
        return ValueError('There is not such Competition')

    if competition.type == 'double':
        return render_double_elimination(request, competition_id)
    elif competition.type == 'league':
        return render_league(request, competition_id)


@login_required()
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
    print(win_matches)
    print(lose_matches)
    # return [win_matches, lose_matches]
    return render(request, 'scoreboard/bracket.html', {
        'win_matches': win_matches,
        'lose_matches': lose_matches
    })


@login_required()
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
        if cnt >= len(matches):
            break
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
        num_matches_per_week = int((league_size - 1) / 2)
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
    # return [league_scoreboard, league_matches]

    return render(request, 'scoreboard/group_table.html', {
        'league_scoreboard': league_scoreboard,
        'league_matches': league_matches
    })


@csrf_exempt
def report(request):
    logger.debug("Someone calling report")
    if request.META.get('HTTP_AUTHORIZATION') != settings.INFRA_AUTH_TOKEN:
        return HttpResponseBadRequest()
    logger.debug("BODY: " + request.body.decode("utf-8"))
    single_report = json.loads(request.body.decode("utf-8"), strict=False)
    logger.debug("Deserialized json")
    if single_report['operation'] == 'compile':
        if TeamSubmission.objects.filter(infra_compile_token=single_report['id']).count() != 1:
            logger.error('Error while finding team submission in report view')
            return HttpResponseServerError()

        submit = TeamSubmission.objects.get(infra_compile_token=single_report['id'])
        if single_report['status'] == 2:
            submit.infra_compile_token = single_report['parameters'].get('code_compiled_zip', None)
            if submit.status == 'compiling':
                try:
                    logfile = functions.download_file(single_report['parameters']['code_log'])
                except Exception as e:
                    logger.error('Error while download log of compile: %s' % e)
                    return HttpResponseServerError()

                reader = codecs.getreader('utf-8')

                log = json.load(reader(logfile), strict=False)
                if len(log["errors"]) == 0:
                    submit.status = 'compiled'
                    submit.set_final()
                else:
                    submit.status = 'failed'
                    submit.infra_compile_message = '...' + '<br>'.join(error for error in log["errors"])[-1000:]
        elif single_report['status'] == 3:
            submit.status = 'failed'
            submit.infra_compile_message = 'Unknown error occurred maybe compilation timed out'
        submit.save()
        return JsonResponse({'success': True})

    elif single_report['operation'] == 'run':
        logger.debug("Getting run report")
        try:
            single_match = SingleMatch.objects.get(infra_token=single_report['id'])
            logger.debug("Obtained relevant single match")
        except Exception as exception:
            logger.error(exception)
            return HttpResponseBadRequest()
            pass

        if single_report['status'] == 2:
            logger.debug("Report status is OK")
            logfile = functions.download_file(single_report['parameters']['game_log'])
            if logfile is None:
                pass
            single_match.status = 'done'
            single_match.log = logfile
            single_match.update_scores_from_log()
        elif single_report['status'] == 3:
            single_match.status = 'failed'
            single_match.infra_match_message = single_report['log']
        else:
            return JsonResponse({'success': False, 'error': 'Invalid Status.'})
        single_match.save()
        return JsonResponse({'success': True})
    return HttpResponseServerError()
