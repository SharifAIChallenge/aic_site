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
        member1_email = self.cleaned_data['member1']
        member2_email = self.cleaned_data['member2']
        if not valid:
            return valid
        team_name = self.cleaned_data['team_name']
        if Team.objects.filter(name__exact=team_name).exists():
            self._errors['team_name'] = "This name is used by another team!"
            return False
        if member1_email and member2_email and (member1_email == member2_email):
            self.add_error(None, "You can't add same users to your team!")
            return False
        return True

    def save(self, commit=True):
        super().save()

    class Meta:
        model = UserParticipatesOnTeam
        fields = ('team_name', 'member1', 'member2', )