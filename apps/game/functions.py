import random
import string
import threading
import time
import requests
import json

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

    token = compile_result["token"]
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

    token = match["token"]
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


def upload_file(file):
    """
    This function uploads a file to infrastructure synchronously
    :param file: File field from TeamSubmission model
    :return: file token or raises error with error message
    """
    address = '{}/api/storage/new_file/'.format(settings.INFRA_URL)
    files = {'upload_file': file}
    headers = {'Authorization': 'token {}'.format(settings.INFRA_AUTH_TOKEN)}
    response = requests.put(address, files=files, headers=headers)
    if response.status_code == 201:
        return json.loads(response.text)['token']
    raise Exception("Can't upload file, returned {} status code".format(str(response.status_code)))


def download_file(file_token):
    """
    Downloads file from infrastructure synchronously
    :param file_token: the file token obtained already from infra.
    :return: sth that TeamSubmission file field can be assigned to
    """

    # Temporary test file
    return "This is text will be replaced by the real log file"


def compile_submissions(file_tokens, game_id):
    """
        Tell the infrastructure to compile a list of submissions
    :param file_tokens: array of strings
    :param game_id: string
    :return: list of dictionaries each have token, success[, errors] keys
    """
    #

    # Test code
    submits = []
    for file_token in file_tokens:
        submits.append({
            "game": game_id,
            "section": "compile",
            "parameters": {  # TODO : parameters
                "string_parameter1": "parameter1_value",
                "string_parameter2": "parameter2_value",
                "file_parameter1": "file_parameter1_token"
            }
        })

    # Send request to infrastructure to compile them

    compile_details = []  # Get the array from the infrastructure.

    for x in file_tokens:
        gm = {
            "token": random_token(),
            "success": True,
            "errors": ""
        }
        compile_details.append(gm)
        t = threading.Thread(target=compilation_result, args=(gm,))
        t.start()

    return compile_details


def run_matches(matches):
    """
        Tell the infrastructure to run a list of matches (match includes tokens,maps,...)
    :param matches: List of match objects, having these functions:
        get_first_file(): String
        get_second_file: String
        get_maps(): String[]
        get_game_id(): String

        and any other potential parameters
    :return: Returns the list of tokens and success status and errors assigned to the matches
    """

    games = []
    for match in matches:
        games.append({
            "game": "1",  # TODO match.get_game_id(),
            "section": "play",
            "parameters": {  # TODO : parameters
                "string_parameter1": "parameter1_value",
                "string_parameter2": "parameter2_value",
                "file_parameter1": "file_parameter1_token"
            }
        })

    # Send request to infrastructure to compile them

    match_details = []  # Get the array from the infrastructure.

    for x in matches:
        gm = {
            "token": random_token(),
            "success": True,
            "errors": ""
        }
        match_details.append(gm)
        t = threading.Thread(target=match_results, args=(gm,))
        t.start()

    return match_details
