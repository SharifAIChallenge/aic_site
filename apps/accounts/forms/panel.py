from django.forms.models import ModelForm
from django.forms import Form
from django import forms

from apps.game.models import TeamSubmission, Map, Team
from apps.game import functions


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
        # result.set_final()
        result.handle()
        return result


class ChallengeATeamForm(forms.Form):
    # battle_team = forms.ChoiceField(choices=[('t1','t1'), ('t2','t2'), ('t3','t3')])
    # battle_team_maps = forms.ChoiceField(choices=[('m1','m1'), ('m2','m2'), ('m3','m3')])
    def __init__(self, *args, **kwargs):
        super(ChallengeATeamForm, self).__init__(*args, **kwargs)
        self.fields['battle_team_maps'] = forms.ChoiceField(
            choices=get_maps())
        self.fields['battle_team'] = forms.ChoiceField(
            choices=get_teams())
