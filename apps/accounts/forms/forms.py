from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.forms.models import ModelForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from apps.accounts.models import Profile
from apps.accounts.tokens import account_activation_token
from captcha.fields import ReCaptchaField


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'oninvalid': _('CUSTOM_VALIDITY')}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'oninvalid': _('CUSTOM_VALIDITY')}))
    email = forms.EmailField(max_length=254, required=True,
                             widget=forms.TextInput(attrs={'oninvalid': _('CUSTOM_VALIDITY')}))
    organization = forms.CharField(max_length=255, required=True,
                                   widget=forms.TextInput(attrs={'oninvalid': _('CUSTOM_VALIDITY')}))
    position = forms.CharField(max_length=255, required=False,
                               widget=forms.TextInput(attrs={'oninvalid': _('CUSTOM_VALIDITY')}))
    phone_regex = RegexValidator(regex=r'^\d{8,15}$',
                                 message=_("Please enter your phone number correctly!"))
    phone_number = forms.CharField(validators=[phone_regex], required=True)
    age = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'oninvalid': _('CUSTOM_VALIDITY')}))
    confirm_data = forms.BooleanField(initial=True, required=False)
    captcha = ReCaptchaField()

    def is_valid(self):
        if not super().is_valid():
            return False
        if not settings.ENABLE_REGISTRATION:
            self.add_error(None, _('Registration is closed. See you next year.'))
            return False
        return True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
            domain = get_current_site(self.request)
            email_text = render_to_string('email/acc_active.txt', {
                'user': user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            email_html = render_to_string('email/acc_active.html', {
                'user': user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })

            profile = Profile(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                organization=self.cleaned_data['organization'],
                age=self.cleaned_data['age'],
                position=self.cleaned_data['position'],
                confirm_data = self.cleaned_data['confirm_data'],
            )
            profile.save()

            send_mail(subject='Activate Your Account',
                      message=email_text,
                      from_email='Sharif AI Challenge <info@aichallenge.ir>',
                      recipient_list=[user.email],
                      fail_silently=False,
                      html_message=email_html
                      )

        return user

    class Meta:
        model = User
        fields = (
        'username', 'first_name', 'last_name', 'organization', 'position', 'age', 'phone_number', 'email', 'password1',
        'password2')


class UpdateProfileForm(ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label=_('First name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Last name'))

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        if self.instance:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user  = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'first_name_eng', 'last_name_eng', 'national_code', 'phone_number', 'organization')
