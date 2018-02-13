import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from .game import Game
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from apps.accounts.models import Team
# from apps.game.models.competition import Participant


import logging

logger = logging.getLogger(__name__)


class Challenge(models.Model):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=2048)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    registration_start_time = models.DateTimeField()
    registration_end_time = models.DateTimeField()
    registration_open = models.BooleanField()
    team_size = models.IntegerField()
    entrance_price = models.IntegerField()  # In Toomans, 0 for free
    game = models.ForeignKey(Game)
    is_submission_open = models.BooleanField(null=False, blank=False,default=False)

    def __str__(self):
        return self.title

    def can_register(self):
        return self.registration_open  # and (current time between reg_start_time and reg_end_time)

    def open_registration(self):
        self.registration_open = True
        self.save()

    def close_registration(self):
        self.registration_open = False
        self.save()


class TeamParticipatesChallenge(models.Model):
    team = models.ForeignKey(Team, related_name='challanges')
    challenge = models.ForeignKey(Challenge, related_name='teams')

    class Meta:
        unique_together = ('team', 'challenge')
        verbose_name_plural = 'Team Participates In Challenges'

    def __str__(self):
        team_name = ugettext('None')
        if self.team is not None:
            team_name = str(self.team)
        challenge_name = ugettext('None')
        if self.challenge is not None:
            challenge_name = str(self.challenge)
        return ugettext('Team: ') + team_name + ' ' + ugettext('Challenge: ') + challenge_name

    def all_members_accepted(self):
        """
        :rtype: bool
        """
        user_participations = self.team.participants.all()
        ok = True
        for user_participation in user_participations:
            ok &= UserAcceptsTeamInChallenge.objects.filter(team=self, user=user_participation.user).exists()
        return ok

    def has_payed(self):
        """
        :rtype: bool
        """
        pass

    def get_final_submission(self):
        """
        :rtype: TeamSubmission
        """
        try:
            return TeamSubmission.objects.filter(team=self, is_final=True).first()
        except TeamSubmission.DoesNotExist:
            return None

    def itself(self):
        return self.get_final_submission()


class UserAcceptsTeamInChallenge(models.Model):
    team = models.ForeignKey(TeamParticipatesChallenge, related_name='users_acceptance')
    user = models.ForeignKey(User, related_name='accepted_teams')

    class Meta:
        unique_together = ('team', 'user')


def get_submission_file_directory(instance, filename):
    return os.path.join(instance.team.id.__str__(), filename + uuid.uuid4().__str__() + '.zip')


class TeamSubmission(models.Model):
    LANGUAGE_CHOICES = (
        ('cpp', _('C++')),
        ('java', _('Java')),
        ('py3', _('Python 3'))
    )

    STATUS_CHOICES = (
        ('uploading', _('Uploading')),
        ('uploaded', _('Uploaded')),
        ('compiling', _('Compiling')),
        ('compiled', _('Compiled')),
        ('failed', _('Failed'))
    )

    team = models.ForeignKey(TeamParticipatesChallenge, related_name='submissions')
    file = models.FileField(upload_to=get_submission_file_directory)
    time = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)
    language = models.CharField(max_length=128, choices=LANGUAGE_CHOICES, default='java')
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default='uploading')
    infra_compile_message = models.CharField(max_length=1023, null=True, blank=True)
    infra_token = models.CharField(max_length=256, null=True, blank=True, unique=True)
    infra_compile_token = models.CharField(max_length=256, null=True, blank=True, unique=True)

    def __str__(self):
        return str(self.id) + ' team: ' + str(self.team) + ' is final: ' + str(self.is_final)

    def set_final(self):
        """
            Use this method instead of changing the is_final attribute directly
            This makes sure that only one instance of TeamSubmission has is_final flag set to True
        """
        if self.status != 'compiled':
            raise ValueError(_('This submission is not compiled yet.'))
        TeamSubmission.objects.filter(is_final=True, team=self.team).update(is_final=False)
        self.is_final = True
        self.save()

    def itself(self):
        return self

    def handle(self):
        try:
            self.upload()
            self.compile()
        except Exception as error:
            logger.error(error)

    def upload(self):
        from apps.game import functions
        self.infra_token = functions.upload_file(self.file)
        self.status = 'uploaded'
        self.save()

    def compile(self):
        from apps.game import functions
        result = functions.compile_submissions([self])
        if result[0]['success']:
            self.status = 'compiling'
            self.infra_compile_token = result[0]['run_id']
        else:
            logger.error(result[0][self.infra_token]['errors'])
        self.save()
