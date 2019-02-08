from datetime import timedelta, datetime

from django import forms
from django.conf import settings
from django.db.models import Q
from django.forms.models import ModelForm
from django.utils.timezone import utc
from django.utils.translation import ugettext, ugettext_lazy as _

from apps.game.models import TeamSubmission, Map, Team, TeamParticipatesChallenge, Match, Competition, Participant, \
    SingleMatch

import logging

logger = logging.getLogger(__name__)


def get_maps(competition):
    maps = [('', '----')]
    for map in Map.objects.all():
        if competition.id in [competition.id for competition in map.competitions.all()]:
            maps.append((map.id, map.name))  # id will pass
    return maps


def get_submitted_teams(challenge):
    teams = [('', '----')]
    for team_participates_in_challenge in challenge.teams.all():
        if team_participates_in_challenge.submissions.filter(is_final=True).exists():
            teams.append(
                (team_participates_in_challenge.id, team_participates_in_challenge.team.name))  # name will pass
    return teams


class SubmissionForm(ModelForm):
    class Meta:
        model = TeamSubmission
        fields = ('file', 'language', 'team')

    def is_valid(self):
        is_valid = super().is_valid()
        if not is_valid:
            return False
        if not settings.ENABLE_SUBMISSION:
            self.add_error(None, _('Submission is closed.'))
            return False
        if not self.cleaned_data['team'].challenge.is_submission_open:
            return False

        submissions = self.cleaned_data['team'].submissions

        if submissions.exists() and datetime.now(utc) - submissions.order_by('-time')[0].time < timedelta(minutes=settings.TEAM_SUBMISSION_TIME_DELTA):
            self.add_error(
                None,
                _("You have to wait at least %(minutes)s minutes between each submission!") %
                {'minutes': settings.TEAM_SUBMISSION_TIME_DELTA}
            )
            return False

        if self.cleaned_data['file'].size > 5242880:
            self.add_error('file', _('Max file size is 5MB.'))
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
            choices=get_maps(self.participation.challenge.competitions.get(type='friendly')))
        self.fields['battle_team'] = forms.ChoiceField(
            choices=get_submitted_teams(self.participation.challenge))

    def is_valid(self):
        if not super().is_valid():
            return False
        if self.participation.get_final_submission() is None:
            self.add_error(None, _("First submit a compilable code."))
            return False
        if self.user.id not in [participant.user.id for participant in self.participation.team.participants.all()]:
            self.add_error(None, _("You have to be one of participants."))
            return False
        friendly_competition = Competition.objects.get(challenge=self.participation.challenge, type='friendly')
        friendly_matches = Match.objects.filter(competition=friendly_competition,
                                                part1__object_id=self.participation.id)
        if friendly_matches.exists():
            last_submission = friendly_matches.order_by('-time')[0]
            if datetime.now(utc) - last_submission.time < timedelta(minutes=settings.SINGLE_MATCH_SUBMISSION_TIME_DELTA):
                self.add_error(
                    None,
                    _("You have to wait at least %(minutes)s minutes between each match!") %
                    {'minutes': settings.SINGLE_MATCH_SUBMISSION_TIME_DELTA}
                )
                return False
        return True

    def save(self, commit=True):
        challenge = self.participation.challenge
        competition = Competition.objects.filter(
            challenge=challenge,
            type='friendly'
        ).first()

        second_team_participation = TeamParticipatesChallenge.objects.filter(
            id=self.cleaned_data['battle_team']).first()

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

        single_match = SingleMatch(match=match, map=competition_map, status='waitacc')
        if commit:
            single_match.save()


