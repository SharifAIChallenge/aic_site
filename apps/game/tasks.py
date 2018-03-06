from celery import shared_task

import logging

logger = logging.getLogger(__name__)


@shared_task
def handle_submission(submission_id):
    from apps.game.models import TeamSubmission
    team_submission = TeamSubmission.objects.get(submission_id)
    try:
        team_submission.upload()
        team_submission.compile()
    except Exception as error:
        logger.error(error)
