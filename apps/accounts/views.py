from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from apps.accounts.forms.team_forms import CreateTeamForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
# Create your views here.
from django.views.generic import FormView, RedirectView

from apps.accounts.forms.forms import SignUpForm, UpdateProfileForm
from apps.accounts.forms.panel import SubmissionForm
from apps.accounts.models import Profile, Team, UserParticipatesOnTeam
from apps.game.models import TeamParticipatesChallenge, TeamSubmission
import json
from apps.game.models.challenge import TeamParticipatesChallenge
from apps.game.models.challenge import Challenge

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


class UpdateProfileView(LoginRequiredMixin, generic.UpdateView):
    form_class = UpdateProfileForm
    success_url = '/'
    template_name = 'accounts/update_profile.html'
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)


@login_required
def panel(request, participation_id=None):
    if participation_id is not None:
        participation = TeamParticipatesChallenge.objects.get(id=participation_id)
    else:
        participation = None

    page = request.GET.get('page', 1)

    context = {
        'submissions': Paginator(
            TeamSubmission.objects.filter(team=participation_id).order_by('-id'),
            10
        ).page(page),
        'participation': participation,
        'invitations': [],
        'accepted_participations': []
    }

    all_participations = TeamParticipatesChallenge.objects.all()
    for challenge_participation in all_participations:
        if not UserAcceptsTeamInChallenge.objects.filter(team=challenge_participation, user=request.user).exists():
            context['invitations'].append(challenge_participation)
        else:
            context['accepted_participations'].append(challenge_participation.team)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = SubmissionForm()
        form.fields['team'].queryset = TeamParticipatesChallenge.objects.filter(
            team__in=context['accepted_participations']
        )
        if participation is not None:
            form.initial['team'] = participation
            form.fields['team'].empty_label = None

    context['form'] = form
    if participation is not None:
        context['challenge_teams'] = [team_part.team for team_part in
                                      TeamParticipatesChallenge.objects.filter(challenge=participation.challenge)]
    return render(request, 'accounts/panel.html', context)


def set_final_submission(request, submission_id):
    submission = TeamSubmission.objects.get(id=submission_id)
    submission.set_final()
    data = {'success': True, 'submission_id': submission_id}
    return HttpResponse(json.dumps(data))


def accept_participation(request, participation_id):
    accept = UserAcceptsTeamInChallenge(team_id=participation_id, user=request.user)
    accept.save()
    other_invitations = TeamParticipatesChallenge.objects.filter(challenge=accept.team.challenge)
    for invitation in other_invitations:
        if invitation.id != int(participation_id):
            invitation.delete()
    return redirect('accounts:panel', participation_id)


def reject_participation(request, participation_id):
    TeamParticipatesChallenge.objects.get(id=participation_id).delete()
    return redirect('accounts:panel')



@login_required()
def create_team(request, challenge_id):
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            member1_email = request.POST['member1']
            member2_email = request.POST['member2']
            team_name = form.cleaned_data.get('team_name')
            team = Team(name=team_name)
            team.save()
            challenge = Challenge.objects.get(id=challenge_id)
            team_challenge = TeamParticipatesChallenge(team=team, challenge=challenge)
            team_challenge.save()

            if member1_email and member2_email:
                member1 = User.objects.get(email__exact=member1_email)
                member2 = User.objects.get(email__exact=member2_email)
                user_team0 = UserParticipatesOnTeam(team=team, user=request.user)
                user_team0.save()
                user_team1 = UserParticipatesOnTeam(team=team, user=member1)
                user_team1.save()
                user_team2 = UserParticipatesOnTeam(team=team, user=member2)
                user_team2.save()
                return redirect('accounts:success_create_team')
            elif (not member2_email) and member1_email:
                member1 = User.objects.get(email__exact=member1_email)
                user_team0 = UserParticipatesOnTeam(team=team, user=request.user)
                user_team0.save()
                user_team1 = UserParticipatesOnTeam(team=team, user=member1)
                user_team1.save()
                return redirect('accounts:success_create_team')
            elif (not member2_email) and (not member1_email):
                user_team0 = UserParticipatesOnTeam(team=team, user=request.user)
                user_team0.save()
                return redirect('accounts:success_create_team')
    else:
        form = CreateTeamForm()
    return render(request, 'accounts/create_team.html', {'form': form
        , 'users': User.objects.exclude(username__exact=request.user.username)
        , 'username': request.user.username})


def success_create_team(request):
    return render(request, 'accounts/success_create_team.html')
