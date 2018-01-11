import random
import string


def random_token():
    chars = string.ascii_letters + string.digits
    return ''.join((random.choice(chars)) for i in range(15))


def upload_file(file):
    # Tell infrastructure to upload file.
    # Returns the token of the uploaded file.

    # Request to upload file
    return random_token()


def download_file(file_token):
    # Download the file of a match (with file's) from the infrastructure.
    # Returns the file.

    # Request and get the log file
    return "This is text will be replaced by the real log file"


def compile_submissions(submission_tokens, game_id):
    # Tell the infrastructure to compile a list of submission

    submits = []
    for submission_token in submission_tokens:
        submits.append({
            "game": game_id,
            "section": "compile",
            "parameters": {
                "string_parameter1": "parameter1_value",
                "string_parameter2": "parameter2_value",
                "file_parameter1": "file_parameter1_token"
            }
        })

    # Send request to infrastructure to compile them
    # TODO : A thread to call compile results

    compile_details = []  # Get the array from the infrastructure.

    for x in submission_tokens:
        compile_details.append({
            "token": random_token(),
            "success": True,
            "errors": ""
        })

    return compile_details


def run_matches(matches, game_id):
    # Tell the infrastructure to run a list of matches (match includes tokens,maps,...)
    # Returns the list of tokens and success status and errors assigned to the matches

    games = []
    for match in matches:
        games.append({
            "game": game_id,
            "section": "play",
            "parameters": {
                "string_parameter1": "parameter1_value",
                "string_parameter2": "parameter2_value",
                "file_parameter1": "file_parameter1_token"
            }
        })

    # Send request to infrastructure to compile them
    # TODO : A thread to call matches results

    match_details = []  # Get the array from the infrastructure.

    for x in matches:
        match_details.append({
            "token": random_token(),
            "success": True,
            "errors": ""
        })

    return match_details


def compilation_result(compile_result):
    # Returns compilation results.

    token = compile_result["token"]
    success = compile_result["success"]
    errors = ""
    parameters = {}

    if success is False:
        errors = ""
    else:
        parameters = {}

    # TODO : update result in model
    pass


def match_results(match):
    # Return matches results.

    token = match["token"]
    success = match["success"]
    errors = ""
    parameters = {}

    if success is False:
        errors = ""
    else:
        parameters = {}

    # TODO : update result in model
    pass


def is_compile_report(game):
    # TODO
    return True


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
