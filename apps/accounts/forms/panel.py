from django.forms.models import ModelForm

from apps.game.models import TeamSubmission


class SubmissionForm(ModelForm):
    class Meta:
        model = TeamSubmission
        fields = ('file', 'language', 'team')

    def save(self, commit=True):
        result = super().save(commit)
        result.set_final()
        return result
