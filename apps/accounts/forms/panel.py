from django.forms.models import ModelForm
from django.forms import Form

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
