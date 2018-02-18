from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Profile

class UserCompletionForm(forms.ModelForm):
    mobile_number = forms.CharField(max_length=30, required=True, help_text='Optional.')
    national_code = forms.CharField(max_length=10, required=True, help_text='Optional.')

    class Meta:
        model = Profile
        fields = ('phone_number', 'mobile_number', 'national_code')

    def clean_national_code(self):
        national_code = self.cleaned_data['national_code']
        if not str(national_code).isnumeric():
            raise forms.ValidationError(_('Entered national code is not valid'))