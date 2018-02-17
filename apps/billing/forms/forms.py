from django import forms

from apps.accounts.models import Profile


class UserCompletionForm(forms.ModelForm):
    mobile_number = forms.CharField(max_length=30, required=True, help_text='Optional.')


    class Meta:
        model = Profile
        fields = ('phone_number', 'mobile_number', 'national_code')