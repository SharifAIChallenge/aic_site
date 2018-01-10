from django.forms import ModelForm
from django import forms

from apps.accounts.models import Team, UserParticipatesOnTeam


class CreateTeamForm(ModelForm):
    team_name = forms.CharField(max_length=30, required=True, help_text='Required,Choose a suitable name for your team')

    def save(self, commit=True):
        super().save(commit=False)

    class Meta:
        model = Team
        fields = ('team_name',)


class AddMemberTeamForm(ModelForm):
    member = forms.CharField(max_length=30, required=False)

    def save(self, commit=True):
        super().save()

    class Meta:
        model = UserParticipatesOnTeam
        fields = ('member',)
