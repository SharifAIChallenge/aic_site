import logging

from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Team
from apps.game.models import TeamSubmission

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'intro/index.html', {
        'no_sidebar': False,
        'users_count': User.objects.count(),
        'submits_count': TeamSubmission.objects.count(),
        'teams_count': Team.objects.count(),
    })


def faq(request):
    return render(request, 'intro/faq.html')


def not_found(request):
    logger.error("hello")
    logger.info("hello")
    logger.debug("hello")
    logger.warning("hello")
    return render(request, '404.html')


def staffs(request):
    return render(request, 'intro/staffs.html')
