from celery import shared_task

from apps.game.models import TeamSubmission

import logging

logger = logging.getLogger(__name__)


@shared_task
def handle_submission(submission_id):
    submission = TeamSubmission.objects.get(id=submission_id)
    try:
        submission.upload()
        submission.compile()
    except Exception as error:
        logger.error(error)
