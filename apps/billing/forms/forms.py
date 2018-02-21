from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Profile


class UserCompletionForm(forms.ModelForm):
    # def save(self, commit=True):
    #     profile = super().save(commit=False)
    #     profile.phone_number = self.cleaned_data['phone_number']
    #     profile.national_code = self.cleaned_data['national_code']
    #     profile.tel_number = self.cleaned_data['tel_number']
    #
    #     if commit:
    #         profile.save()
    #     return profile

    class Meta:
        model = Profile
        fields = ('phone_number', 'tel_number', 'national_code')

    def clean_national_code(self):
        national_code = self.cleaned_data['national_code']
        if not str(national_code).isnumeric():
            raise forms.ValidationError(_('Entered national code is not valid'))
        return national_code
