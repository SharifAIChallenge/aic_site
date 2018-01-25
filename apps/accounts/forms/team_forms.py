from django.forms import ModelForm, Form
from django import forms
from apps.accounts.models import Team, UserParticipatesOnTeam, User
from apps.game.models import Challenge, TeamParticipatesChallenge
from apps.game.models.challenge import UserAcceptsTeamInChallenge
from django.utils.translation import ugettext_lazy as _


class CreateTeamForm(Form):
    team_name = forms.CharField(max_length=30, required=True,
                                help_text=_('Required,Choose a suitable name for your team'))
    member1 = forms.CharField(max_length=30, required=False)
    member2 = forms.CharField(max_length=30, required=False)
    challenge_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def is_valid(self):
        valid = super(Form, self).is_valid()
        member1_email = self.cleaned_data['member1']
        member2_email = self.cleaned_data['member2']
        if not valid:
            return valid
        team_name = self.cleaned_data['team_name']
        if Team.objects.filter(name__exact=team_name).exists():
            self._errors['team_name'] = _("This name is used by another team!")
            return False
        if member1_email and member2_email and (member1_email == member2_email):
            self.add_error(None, _("You can't add same users to your team!"))
            return False
        if UserAcceptsTeamInChallenge.objects.filter(user__email__in=[self.user.email, member1_email, member2_email],
                                                     team__challenge_id=self.cleaned_data['challenge_id']).count() > 0:
            self.add_error(None, _("Some of users are already participated in the challenge!"))
            return False
        return True

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        member1_email = self.cleaned_data['member1']
        member2_email = self.cleaned_data['member2']
        team_name = self.cleaned_data.get('team_name')
        team = Team(name=team_name)
        if commit:
            team.save()
        challenge = Challenge.objects.get(id=self.cleaned_data['challenge_id'])
        team_challenge = TeamParticipatesChallenge(team=team, challenge=challenge)
        if commit:
            team_challenge.save()

        if member1_email and member2_email:
            member1 = User.objects.get(email__exact=member1_email)
            member2 = User.objects.get(email__exact=member2_email)
            user_team0 = UserParticipatesOnTeam(team=team, user=self.user)
            user_team1 = UserParticipatesOnTeam(team=team, user=member1)
            user_team2 = UserParticipatesOnTeam(team=team, user=member2)
            if commit:
                user_team0.save()
                user_team1.save()
                user_team2.save()
        elif (not member2_email) and member1_email:
            member1 = User.objects.get(email__exact=member1_email)
            user_team0 = UserParticipatesOnTeam(team=team, user=self.user)
            user_team1 = UserParticipatesOnTeam(team=team, user=member1)
            if commit:
                user_team0.save()
                user_team1.save()
        elif (not member2_email) and (not member1_email):
            user_team0 = UserParticipatesOnTeam(team=team, user=self.user)
            if commit:
                user_team0.save()

    class Meta:
        model = UserParticipatesOnTeam
        fields = ('team_name', 'member1', 'member2',)
