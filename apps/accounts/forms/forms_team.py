from django.forms import ModelForm
from django import forms

from apps.accounts.models import Team, UserParticipatesOnTeam


class CreateTeamForm(ModelForm):
    team_name = forms.CharField(max_length=30, required=True, help_text='Required,Choose a suitable name for your team')

    def save(self, commit=True):
        user = super().save(commit=False)
        team_name = self.cleaned_data['team_name']
        team = Team(name=team_name)

        if commit:
            team.save()
#            team_user = UserParticipatesOnTeam(user=user, team=team)
#            team_user.save()
        return team

    class Meta:
        model = Team
        fields = ('team_name',)
