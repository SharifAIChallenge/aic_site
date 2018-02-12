from datetime import timedelta, datetime

from django import forms
from django.conf import settings
from django.forms.models import ModelForm
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from apps.game.models import TeamSubmission, Map, Team, TeamParticipatesChallenge, Match, Competition, Participant, \
    SingleMatch

import logging

logger = logging.getLogger(__name__)


def get_maps():
    maps = []
    maps.append(('', '----'))  # nothing
    for i in Map.objects.all():  # TODO : get all from a competition
        maps.append((i.id, i.name))  # id will pass
    return maps


def get_teams():
    teams = []
    teams.append(('', '----'))  # nothing
    for i in Team.objects.all():  # TODO : get all from a competition
        teams.append((i.id, i.name))  # name will pass
    return teams


class SubmissionForm(ModelForm):
    class Meta:
        model = TeamSubmission
        fields = ('file', 'language', 'team')

    def is_valid(self):
        is_valid = super().is_valid()
        if not is_valid:
            return False
        if not self.cleaned_data['team'].challenge.is_submission_open:
            return False
        return True

    def save(self, commit=True):
        result = super().save(commit)
        result.handle()
        return result


class ChallengeATeamForm(forms.Form):
    def __init__(self, user, participation, *args, **kwargs):
        super(ChallengeATeamForm, self).__init__(*args, **kwargs)
        self.user = user
        self.participation = participation
        self.fields['battle_team_maps'] = forms.ChoiceField(
            choices=get_maps())
        self.fields['battle_team'] = forms.ChoiceField(
            choices=get_teams())

    def is_valid(self):
        if not super().is_valid():
            return False
        if self.user.id not in [participant.user.id for participant in self.participation.team.participants.all()]:
            self.add_error(None, _("You have to be one of participants."))
            return False
        submissions = TeamSubmission.objects.filter(team__exact=self.participation)
        last_submission = submissions.order_by('-time')[0]
        if datetime.now(utc) - last_submission.time < timedelta(minutes=settings.SINGLE_MATCH_SUBMISSION_TIME_DELTA):
            self.add_error(None, _("You have to wait at least one hour between each match"))
            return False
        return True

    def save(self, commit=True):
        try:
            challenge = self.participation.challenge
            competition = Competition.objects.filter(
                challenge=challenge,
                type='friendly'
            ).first()

            second_team = Team.objects.filter(id=self.cleaned_data['battle_team']).first()
            second_team_participation = TeamParticipatesChallenge.objects.filter(team=second_team, challenge=challenge).first()

            first_participant = Participant()
            first_participant.depend = self.participation
            first_participant.submission = self.participation.get_final_submission()
            if commit:
                first_participant.save()

            second_participant = Participant()
            second_participant.depend = second_team_participation
            second_participant.submission = second_team_participation.get_final_submission()
            if commit:
                second_participant.save()

            match = Match(part1=first_participant, part2=second_participant, competition=competition)
            if commit:
                match.save()

            competition_map = Map.objects.filter(id=self.cleaned_data['battle_team_maps']).first()

            single_match = SingleMatch(match=match, map=competition_map)
            if commit:
                single_match.save()

            single_match.handle()

        except Exception as e:
            logger.error("Team failed to submit: " + str(e))
