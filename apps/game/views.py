import logging
import json

from django.http import HttpResponseServerError, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from apps.game import functions
from apps.game.models import Competition, SingleMatch
from apps.game.models import TeamSubmission

logger = logging.getLogger(__name__)


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
    # return render(request, 'double_score_board.html', {'win_matches': win_matches,
    #                                                    'lose_matches': lose_matches}
    #


@csrf_exempt
def report(request):
    if request.META.get('HTTP_AUTHORIZATION') != settings.INFRA_AUTH_TOKEN:
        return HttpResponseBadRequest()
    single_report = json.loads(request.body.decode("utf-8"))
    client, schema = functions.create_infra_client()

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

    elif single_report['operation'] == 'run':
        try:
            single_match = SingleMatch.objects.get(infra_token=single_report['id'])
        except Exception as exception:
            pass
            # continue
        if single_report['status'] == 2:
            logfile = client.action(schema, ['storage', 'get_file', 'read'],
                                    params={'token': single_report['parameters']['game_log']})
            if logfile is None:
                pass
                # continue
            single_match.log = logfile
            single_match.update_scores_from_log()
            single_match.save()
            return JsonResponse({'success': True})
    return HttpResponseServerError()
