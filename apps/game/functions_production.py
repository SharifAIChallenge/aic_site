import random
import string
import threading
import time
import uuid

import coreapi
from django.conf import settings

from apps.game.models import TeamSubmission, Match


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
    parameters = {}

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
    """
    This function uploads a file to infrastructure synchronously
    :param file: File field from TeamSubmission model
    :return: file token or raises error with error message
    """
    client, schema = create_infra_client()
    response = client.action(schema,
                             ['storage', 'new_file', 'update'],
                             params={'file': file})
    return response['token']


def download_file(file_token):
    """
    Downloads file from infrastructure synchronously
    :param file_token: the file token obtained already from infra.
    :return: sth that TeamSubmission file field can be assigned to
    """
    client, schema = create_infra_client()
    return client.action(schema,
                         ['storage', 'get_file', 'read'],
                         params={'token': file_token})


def compile_submissions(submissions):
    """
        Tell the infrastructure to compile a list of submissions
    :param file_tokens: array of strings
    :param game_id: string
    :return: list of dictionaries each have token, success[, errors] keys
    """
    #

    # Test code
    requests = list()
    for submission in submissions:
        requests.append({
            "game": submission.team.challenge.game.infra_token,
            "operation": "compile",
            "parameters": {
                "language": submission.language,
                "code_zip": submission.infra_token
            }
        })

    # Send request to infrastructure to compile them

    client, schema = create_infra_client()

    compile_details = client.action(schema,
                                    ['run', 'run', 'create'],
                                    params={
                                        'data': requests
                                    })
    print(compile_details)
    return compile_details


def run_matches(single_matches):
    """
        Tell the infrastructure to run a list of single_matches (single_match includes tokens,maps,...)
    :param matches: List of single_match objects, having these functions:
        get_first_file(): String
        get_second_file: String
        get_map(): String
        get_game_id(): String

        and any other potential parameters
    :return: Returns the list of tokens and success status and errors assigned to the matches
    """

    games = []
    for single_match in single_matches:
        games.append({
            "game": single_match.get_game_id(),
            "operation": "run",
            "parameters": {
                "server_game_config": single_match.get_map(),
                "client1_id": single_match.match.part1.submission.id,
                "client1_token": str(uuid.uuid4()),
                "client1_code": single_match.get_first_file(),
                "client2_id": single_match.match.part2.submission.id,
                "client2_token": str(uuid.uuid4()),
                "client2_code": single_match.get_second_file(),
            }
        })

    # Send request to infrastructure to compile them

    client, schema = create_infra_client()

    match_details = client.action(schema,
                                  ['run', 'run', 'create'],
                                  params={
                                      'data': games
                                  })

    return match_details
