from django.forms import ModelForm
from django import forms

from apps.accounts.models import Team


class CreateTeamForm(ModelForm):
    team_name = forms.CharField(max_length=30, required=True, help_text='Required,Choose a suitable name for your team')

    def clean(self):
        super().clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        team = Team(name=self.team_name)
        