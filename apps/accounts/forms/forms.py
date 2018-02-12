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
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    organization = forms.CharField(max_length=255, required=True)
    phone_regex = RegexValidator(regex=r'^\d{8,15}$',
                                 message=_("Please enter your phone number correctly!"))
    phone_number = forms.CharField(validators=[phone_regex], required=False)
    age = forms.IntegerField(required=True)
    captcha = ReCaptchaField()

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
            send_mail(subject='Activate Your Account',
                      message=email_text,
                      from_email='Sharif AI Challenge <info@aichallenge.ir>',
                      recipient_list=[user.email],
                      fail_silently=False,
                      html_message=email_html
                      )
            profile = Profile(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                organization=self.cleaned_data['organization'],
                age=self.cleaned_data['age']
            )
            profile.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'organization','age', 'phone_number', 'email', 'password1', 'password2')


class UpdateProfileForm(ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    age = forms.IntegerField(required=True)
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(required=False, widget=forms.PasswordInput)

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            self.add_error('password1', 'password error')

    def save(self, commit=True):
        user = super().save(commit=False)
        profile = user.profile
        profile.phone_number = self.cleaned_data['phone_number']
        profile.age = self.cleaned_data['age']
        profile.organization = self.cleaned_data['organization']

        if commit:
            user.save()
            profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email','phone_number','age', 'password1', 'password2')
