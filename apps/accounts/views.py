from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.views import generic
# Create your views here.
from django.views.generic import FormView, RedirectView

from apps.accounts.forms.forms import SignUpForm, UpdateProfileForm
from apps.accounts.forms.panel import SubmissionForm
from apps.accounts.models import Profile, Team, UserParticipatesOnTeam
from apps.game.models import TeamParticipatesChallenge


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


def panel(request, participation_id=None):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            pass
    else:
        form = SubmissionForm()
        form.fields['team'].queryset = TeamParticipatesChallenge.objects.filter(
            team__in=[participation.team for participation in UserParticipatesOnTeam.objects.filter(user=request.user)]
        )
        if participation_id is not None:
            form.instance.team = TeamParticipatesChallenge.objects.get(id=participation_id)
        return render(request, 'accounts/panel.html', {'submission_form': form})
