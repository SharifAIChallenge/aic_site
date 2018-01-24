from django.forms.models import ModelForm
from django.forms import Form
from django import forms

from apps.game.models import TeamSubmission
from apps.game import functions


class SubmissionForm(ModelForm):
    class Meta:
        model = TeamSubmission
        fields = ('file', 'language', 'team')

    def save(self, commit=True):
        result = super().save(commit)
        result.set_final()
        result.handle()
        return result


class ChallengeATeamForm(forms.Form):
    battle_team = forms.ChoiceField(choices=[('t1','t1'), ('t2','t2'), ('t3','t3')])
    battle_team_maps = forms.ChoiceField(choices=[('m1','m1'), ('m2','m2'), ('m3','m3')]) # TODO : Dynamic choices


