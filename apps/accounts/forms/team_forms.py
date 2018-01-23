from django.forms import ModelForm, Form
from django import forms
from apps.accounts.models import Team, UserParticipatesOnTeam, User


class CreateTeamForm(Form):
    team_name = forms.CharField(max_length=30, required=True,
                                help_text='Required,Choose a suitable name for your team')
    member1 = forms.CharField(max_length=30, required=False)
    member2 = forms.CharField(max_length=30, required=False)

    def is_valid(self):
        valid = super(Form, self).is_valid()
        if not valid:
            return valid
        team_name = self.cleaned_data['team_name']
        member1_email = self.cleaned_data['member1']
        member2_email = self.cleaned_data['member2']
        if Team.objects.filter(name__exact=team_name).exists():
            self._errors['team_name'] = "this name is used by another team"
            return False
        if member1_email and member2_email:
            if not User.objects.filter(email__exact=member1_email).exists():
                self._errors['member1'] = "there is no user registered with this username"
                return False
            if not User.objects.filter(email__exact=member2_email).exists():
                self._errors['member2'] = "there is no user registered with this username"
                return False
        elif (not member2_email) and member1_email:
            if not User.objects.filter(email__exact=member1_email).exists():
                self._errors['member1'] = "there is no user registered with this username"
                return False
        return True

    def save(self, commit=True):
        super().save()

    class Meta:
        model = UserParticipatesOnTeam
        fields = ('team_name', 'member1', 'member2', )