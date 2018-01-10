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

    file = open('static/play_logs/' + file_token + '.log', 'w')
    # Request and get the log file
    file.write("Mock Log File")
    file.close()


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

    compile_tokens = []  # Get the array from the infrastructure.

    for x in submission_tokens:
        compile_tokens.append(random_token())

    return compile_tokens


def run_matches(matches, game_id):
    # Tell the infrastructure to run a list of matches (match includes tokens,maps,...)
    # Returns the list of tokens assigned to the matches

    games = []
    for submission_token in matches:
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

    match_tokens = []  # Get the array from the infrastructure.

    for x in matches:
        match_tokens.append(random_token())

    return match_tokens


def compilation_results(compile_file):
    # Returns compilation results.

    # TODO

    pass


def matches_results(matches):
    # Return matches results.

    # TODO

    pass


def pull_results():
    # Requests latest results from the infrastructure and updates them

    submits = []
    matches = []

    games = []  # Request updates from the infrastructure.

    for game in games:
        if game["section"] == "compile":
            compilation_results(game)
        elif game["section"] == "play":
            matches_results(game)
