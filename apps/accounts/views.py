from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import request
from django.shortcuts import get_object_or_404
from django.views import generic
# Create your views here.
from django.views.generic import FormView, RedirectView

from apps.accounts.forms.forms import SignUpForm, UpdateProfileForm
from apps.accounts.models import Profile


class SignupView(generic.CreateView):
    form_class = SignUpForm
    success_url = '/accounts/login/'
    template_name = 'accounts/signup.html'


class LoginView(FormView):
    success_url = '/'
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())

        return super(LoginView, self).form_valid(form)


class LogoutView(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class UpdateProfileView(generic.UpdateView):
    form_class = UpdateProfileForm
    success_url = '/'
    template_name = 'accounts/update_profile.html'
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)
