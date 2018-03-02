from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Profile


class UserCompletionForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label=_('First name'))
    last_name = forms.CharField(required=True, label=_('Last name'))

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'phone_number', 'tel_number', 'national_code', 'organization')

    def clean_national_code(self):
        national_code = self.cleaned_data['national_code']
        if not str(national_code).isnumeric():
            raise forms.ValidationError(_('Entered national code is not valid'))
        return national_code

    def save(self, commit=True):
        result = super().save(commit)
        result.user.first_name = self.cleaned_data['first_name']
        result.user.last_name = self.cleaned_data['last_name']
        if commit:
            result.user.save()

        return result

