

def upload_file(file, lang, game_id):

    # Tell infrastructure to upload and compile file with language lang and game id game_id
    # Returns the token of the submission.
    pass


def compile_submissions(submission_tokens):

    # Tell the infrastructure to compile a list of submissions (probably again)

    pass


def download_log(log_token):

    # Download the log file of a match (with matches' token) from the infrastructure.
    # Returns the log file.

    pass


def run_matches(matches):

    # Tell the infrastructure to run a list of matches (match includes tokens,maps,...)
    # Returns the list of tokens assigned to the matches

    pass


""" APIS : """


def compile_response(compile_results):

    # An API for infrastructure to tell us the compilation results
    # Returns compilation statuses.

    pass


def matches_results(matches_results):

    # An API for infrastructure to tell us the matches results.

    pass
