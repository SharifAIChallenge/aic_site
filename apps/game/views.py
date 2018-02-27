import codecs
import json
import logging

from django.conf import settings
from django.core.files import File
from django.http import HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.game import functions
from apps.game.models import Competition, TeamSubmission, SingleMatch, Challenge
from apps.game.utils import get_scoreboard_table_competition, get_scoreboard_table_tag, \
    get_scoreboard_table_from_single_matches

logger = logging.getLogger(__name__)


def render_scoreboard(request, competition_id):
    competition = Competition.objects.get(pk=int(competition_id))
    if competition is None:
        # error handling in template #
        raise ValueError('There is not such Competition')

    if competition.type == 'league':
        return render_league(request, competition_id)
    if competition.type == 'friendly':
        return render_friendly(request, competition_id)
    if competition.type == 'double':
        return render_double_elimination(request, competition_id)
    return HttpResponse('There is not such Competition!')


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
    # print(win_matches)
    # print(lose_matches)
    # return [win_matches, lose_matches]
    return render(request, 'scoreboard/bracket.html', {
        'win_matches': win_matches,
        'lose_matches': lose_matches
    })


def render_tag(request, tag_name):
    league_scoreboard = get_scoreboard_table_tag(tag_name)

    return render(request, 'scoreboard/match_scoreboard.html', {
        'league_scoreboard': league_scoreboard
    })


def render_friendly(request, competition_id):
    league_scoreboard = get_scoreboard_table_competition(competition_id)

    return render(request, 'scoreboard/match_scoreboard.html', {
        'league_scoreboard': league_scoreboard
    })


def render_league(request, competition_id):
    matches = list(Competition.objects.get(pk=int(competition_id)).matches.all())

    league_scoreboard = get_scoreboard_table_competition(competition_id)
    league_size = len(league_scoreboard)
    # print(matches)
    # print(league_scoreboard)
    # list of matches in a special format ( not a simple list) to pass to template for rendering
    league_matches = []

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

    return render(request, 'scoreboard/group_table.html', {
        'league_scoreboard': league_scoreboard,
        'league_matches': league_matches
    })


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


@csrf_exempt
def report(request):
    if request.META.get('HTTP_AUTHORIZATION') != settings.INFRA_AUTH_TOKEN:
        return HttpResponseBadRequest()

    single_report = json.loads(request.body.decode("utf-8"), strict=False)

    if single_report['operation'] == 'compile':
        if TeamSubmission.objects.filter(infra_compile_token=single_report['id']).count() != 1:
            logger.error('Error while finding team submission in report view')
            return JsonResponse({'success': False})

        submit = TeamSubmission.objects.get(infra_compile_token=single_report['id'])
        try:
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
        except BaseException as error:
            submit.status = 'failed'
            submit.infra_compile_message = 'Unknown error occurred maybe compilation timed out'
            logger.exception(error)
            submit.save()
            return JsonResponse({'success': False})
        submit.save()
        return JsonResponse({'success': True})

    elif single_report['operation'] == 'run':
        try:
            single_match = SingleMatch.objects.get(infra_token=single_report['id'])
            logger.debug("Obtained relevant single match")
        except Exception as exception:
            logger.exception(exception)
            return JsonResponse({'success': False})

        try:
            if single_report['status'] == 2:
                logger.debug("Report status is OK")
                logfile = functions.download_file(single_report['parameters']['game_log'])
                single_match.status = 'done'
                single_match.log.save(name='log', content=File(logfile.file))
                single_match.update_scores_from_log()
            elif single_report['status'] == 3:
                single_match.status = 'failed'
                single_match.infra_match_message = single_report['log']
            else:
                return JsonResponse({'success': False, 'error': 'Invalid Status.'})
        except BaseException as error:
            logger.exception(error)
            single_match.status = 'failed'
            single_match.save()
            return JsonResponse({'success': False})

        single_match.save()
        return JsonResponse({'success': True})
    return HttpResponseServerError()


def game_view(request):
    if request.GET.urlencode().__len__() > 0:
        return redirect(to='/static/game_graphics/game_viewer/index.html?'
                           + request.GET.urlencode()
                        )
    else:
        return redirect(to='/static/game_graphics/game_viewer/index.html')


def map_maker(request):
    return redirect(to='/static/game_graphics/map_maker/index.html')


def render_challenge_league(request, challenge_id):
    single_matches = SingleMatch.objects.filter(
        match__competition__challenge_id=challenge_id,
        match__competition__type='league'
    ).prefetch_related(
        'match').prefetch_related(
        'match__part1__depend__team').prefetch_related(
        'match__part2__depend__team').prefetch_related(
        'match__competition').prefetch_related(
    ).filter(status='done')

    competitions_scoreboard = {}

    for single_match in single_matches:
        competition_id = single_match.match.competition_id
        if competition_id not in competitions_scoreboard:
            competitions_scoreboard[competition_id] = {
                'id': competition_id,
                'name': single_match.match.competition.name,
                'league_scoreboard': None,
                'single_matches': [],
            }
        competitions_scoreboard[competition_id]['single_matches'].append(
            single_match
        )

    competitions_scoreboard = list(competitions_scoreboard.values())
    for competition_data in competitions_scoreboard:
        competition_data['league_scoreboard'] = get_scoreboard_table_from_single_matches(
            competition_data['competition']
        )

    return render(request, 'scoreboard/group_table_challenge.html', {
        'tables': reversed(competitions_scoreboard)
    })
