from datetime import timedelta, datetime

from django import forms
from django.conf import settings
from django.db.models import Q
from django.forms.models import ModelForm
from django.utils.timezone import utc
from django.utils.translation import ugettext, ugettext_lazy as _
from random import randrange, seed
from time import time as curr_time

from apps.game.models import TeamSubmission, Map, Team, TeamParticipatesChallenge, Match, Competition, Participant, \
    SingleMatch

import logging

logger = logging.getLogger(__name__)


def get_maps(competition):
    maps = [('', '----')]
    maps_s = []
    for map in Map.objects.all():
        if competition.id in [competition.id for competition in map.competitions.all()]:
            if map.verified:
                if map.team:
                    maps_s.append((map.id, str(map) ))  # id will pass
                else:
                    maps.append((map.id, str(map) ))  # id will pass
    return maps + maps_s


def get_submitted_teams(challenge, tpc):
    teams = [(-1, _('Random team within your level') )] if tpc.allow_random else [('', '---')]
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

        if self.cleaned_data['file'].size > 20 * 1024 * 1024:
            self.add_error('file', _('Max file size is 20MB.'))
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
            choices=get_submitted_teams(self.participation.challenge, self.participation))

    def is_valid(self):
        if not super().is_valid():
            return False
        if not settings.ENABLE_SUBMISSION:
            self.add_error(None, _('Friendly Match is closed.'))
            return False
        if not self.cleaned_data['team'].challenge.is_submission_open:
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

        if self.cleaned_data['battle_team'] == '-1' and not self.participation.allow_random:
            self.add_error(
                None,
                _("You should allow random match first!")
            )
            return False

        if self.cleaned_data['battle_team'] == '-1' and len(self.participation.challenge.teams.filter(allow_random=True)) <= 1:
            self.add_error(
                None,
                _("The only team ready for random is you!")
            )
            return False
        return True

    def save(self, commit=True):
        challenge = self.participation.challenge
        competition = Competition.objects.filter(
            challenge=challenge,
            type='friendly'
        ).first()

        matches = Match.objects.filter(competition=competition,
                                                part1__object_id=self.participation.id)
        if matches.exists():
            last_submission = matches.order_by('-time')[0]
            if datetime.now(utc) - last_submission.time < timedelta(minutes=settings.SINGLE_MATCH_SUBMISSION_TIME_DELTA):
                raise BaseException("Don't try to fool us")

        print(self.cleaned_data['battle_team'])
        if self.cleaned_data['battle_team'] == '-1':
            teams = []

            for team in self.participation.challenge.teams.all():
                if team.allow_random and team.submissions.filter(is_final=True).exists():
                    teams.append(team)

            teams.sort(key=lambda x: x.team.rate)


            ind = teams.index(self.participation)

            st = max(0, ind - settings.RANDOM_MATCH_RANK_RANGE)
            en = min(ind + settings.RANDOM_MATCH_RANK_RANGE, len(teams))
            seed(curr_time())

            trial = 0
            while trial < 5:
                trial += 1
                second_team_participation = teams[randrange(st, en)]
                if second_team_participation != self.participation:
                    break
            approv = False
        else:
            second_team_participation = TeamParticipatesChallenge.objects.filter(
                id=self.cleaned_data['battle_team']).first()
            approv = True

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

        single_match = SingleMatch(match=match, map=competition_map, status='waitacc' if approv else 'waiting')
        if commit:
            single_match.save()
            if not approv:
                single_match.handle()


