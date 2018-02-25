from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from django.views.generic import FormView, RedirectView
from apps.accounts.forms.forms import SignUpForm
from apps.accounts.tokens import account_activation_token


class SignupView(generic.CreateView):
    form_class = SignUpForm
    success_url = '/accounts/email_sent'
    template_name = 'accounts/profile/signup.html'

    def get_form_class(self):
        form = super().get_form_class()
        form.request = self.request
        return form


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect(to='/accounts/email_confirm')
    else:
        return redirect(to='/accounts/email_invalid')


def email_confirm(request):
    return render(request=request, template_name='email/email_confirm.html')


def email_invalid(request):
    return render(request=request, template_name='email/email_invalid.html')


def email_sent(request):
    return render(request=request, template_name='email/email_sent.html')


class LoginView(FormView):
    success_url = '/accounts/panel'
    form_class = AuthenticationForm
    template_name = 'accounts/profile/login.html'

    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())

        return super(LoginView, self).form_valid(form)


class LogoutView(LoginRequiredMixin, RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
