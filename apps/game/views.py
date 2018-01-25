import json

import coreapi as coreapi
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import render

# Create your views here.
from apps.game.models import TeamSubmission


def report(request):
    if not request.is_ajax():
        return HttpResponseBadRequest()
    if request.method != 'POST':
        return HttpResponseBadRequest()

    received_json_data = json.loads(request.body)

    if request.META.get('HTTP_AUTHORIZATION') != settings.INFRA_AUTH_TOKEN:
        return HttpResponseBadRequest()

    credentials = {settings.INFRA_IP: 'Token {}'.format(settings.INFRA_AUTH_TOKEN)}
    transports = [coreapi.transports.HTTPTransport(credentials=credentials)]
    client = coreapi.Client(transports=transports)
    schema = client.get(settings.INFRA_API_SCHEMA_ADDRESS)

    reports = request

    for single_report in reports:
        if single_report['operation'] == 'compile':
            if len(TeamSubmission.objects.filter(infra_token=single_report['id'])) == 0:
                continue
            submit = TeamSubmission.objects.get(infra_token=single_report['id'])
            if single_report['status'] == 2:
                submit.infra_compile_token = single_report['parameters']['code_compiled_zip']
                if submit.status == 'compiling':
                    logfile = client.action(schema, ['storage', 'get_file', 'read'],
                                            params={'token': single_report['parameters']['code_log']})
                    if logfile is None:
                        continue
                    log = json.loads(logfile.read())
                    if len(log["errors"]) == 0:
                        submit.status = 'compiled'
                    else:
                        submit.status = 'failed'
                        submit.infra_compile_message = '\n'.join(error for error in log["errors"])
            elif single_report['status'] == 3:
                submit.status = 'failed'
                submit.infra_compile_message = 'Unknown error occurred maybe compilation timed out'
            submit.save()
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
            pass
