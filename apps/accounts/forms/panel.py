from django.forms.models import ModelForm

from apps.game.models import TeamSubmission


class SubmissionForm(ModelForm):
    class Meta:
        model = TeamSubmission
        fields = ('file', 'language', 'is_final', 'team')
