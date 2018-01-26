import os
import random
import string
import threading
import time
import uuid

import coreapi
from django.conf import settings

from apps.game.models import TeamSubmission, Match

test_json = os.path.join(settings.BASE_DIR, 'apps', 'game', 'code_log.json')


def random_token():
    chars = string.ascii_letters + string.digits
    return ''.join((random.choice(chars)) for i in range(15))


def is_compile_report(game):
    return TeamSubmission.objects.filter(infra_token=game["token"]).exists()


def pull_reports():
    # Requests latest results from the infrastructure and updates them

    submits = []
    matches = []

    games = []  # Request updates from the infrastructure.

    for game in games:
        token = game["token"]

        if is_compile_report(game):
            compilation_result(game)
        else:
            match_results(game)


def compilation_result(compile_result):
    time.sleep(0.2)  # one second delay for testing ... (Database errors may occur

    # Returns compilation results.

    token = compile_result["run_id"]
    success = compile_result["success"]
    errors = ""
    parameters = {}

    if success is True:
        errors = "ok"
    else:
        parameters = {}
        errors = "Error occurred"  # TODO : fix errors with the infrastructure

    TeamSubmission.objects.filter(infra_token=token).update(infra_compile_message=errors)


def match_results(match):
    time.sleep(0.2)  # one second delay for testing ... (Database errors may occur

    # Return matches results.

    token = match["run_id"]
    success = match["success"]
    errors = ""
    parameters = {
        'code_compiled_zip': random_token(),
        'code_log': random_token()
    }

    if success is True:
        errors = "ok"
    else:
        parameters = {}
        errors = "Error occurred"  # TODO : fix errors with the infrastructure

    Match.objects.filter(infra_token=token).update(infra_match_message=errors)


"""
    **** Infrastructure API Functions ****
"""


def create_infra_client():
    credentials = {settings.INFRA_IP: 'Token {}'.format(settings.INFRA_AUTH_TOKEN)}
    transports = [coreapi.transports.HTTPTransport(credentials=credentials)]
    client = coreapi.Client(transports=transports)
    schema = client.get(settings.INFRA_API_SCHEMA_ADDRESS)
    return client, schema


def upload_file(file):
    return random_token()


def download_file(file_token):
    return open(test_json)


def compile_submissions(submissions):
    compile_details = []
    for submission in submissions:
        compile_details.append({
            'success': True,
            'run_id': random_token()
        })
    return compile_details


def run_matches(matches):
    matches_details = []
    for match in matches:
        matches_details.append({
            'success': True,
            'run_id': random_token()
        })
    return matches_details
