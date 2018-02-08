from django import forms

from apps.accounts.models import Profile


class UserCompletionForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('phone_number', 'mobile_number', 'national_code')