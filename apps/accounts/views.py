import logging

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.urls import reverse
from apps.accounts.forms.team_forms import CreateTeamForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import generic

from apps.accounts.forms.team_forms import CreateTeamForm, AddParticipationForm
# Create your views here.
from django.views.generic import FormView, RedirectView

from apps.accounts.forms.forms import SignUpForm, UpdateProfileForm
from apps.accounts.forms.panel import SubmissionForm, ChallengeATeamForm
from apps.accounts.models import Profile, Team, UserParticipatesOnTeam
from apps.accounts.tokens import account_activation_token
from apps.game.models import TeamSubmission, SingleMatch, Match, Participant, Map, Competition, ContentType
import json
from apps.game.models.challenge import TeamParticipatesChallenge, UserAcceptsTeamInChallenge
from apps.game.models.challenge import Challenge

from apps.game.models.challenge import UserAcceptsTeamInChallenge

logger = logging.getLogger(__name__)


class SignupView(generic.CreateView):
    form_class = SignUpForm
    success_url = '/accounts/email_sent'
    template_name = 'accounts/signup.html'

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
    template_name = 'accounts/login.html'

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


class UpdateProfileView(LoginRequiredMixin, generic.UpdateView):
    form_class = UpdateProfileForm
    success_url = '/accounts/panel'
    template_name = 'accounts/update_profile.html'
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)


@login_required
def panel(request, participation_id=None):
    if participation_id is not None:
        try:
            participation = TeamParticipatesChallenge.objects.get(
                id=participation_id,
                team__participants__user=request.user
            )
        except TeamParticipatesChallenge.DoesNotExist:
            return redirect('accounts:panel')
    else:
        participation = None

    page = request.GET.get('page', 1)
    context = {
        'submissions': Paginator(
            TeamSubmission.objects.filter(team=participation_id).order_by('-id'),
            10
        ).page(page),
        'participation': participation,
        'participation_members': [
            (
                user_part.user,
                not UserAcceptsTeamInChallenge.objects.filter(
                    user=user_part.user,
                    team__team=participation.team
                ).exists()
            )
            for user_part in participation.team.participants.all()] if participation else [],
        'challenges': Challenge.objects.all(),
        'invitations': [],
        'accepted_participations': []
    }

    all_participations = TeamParticipatesChallenge.objects.filter(
        team__participants__user=request.user
    )
    if all_participations.count() > 0 and participation is None:
        return redirect('accounts:panel', all_participations.first().id)
    for challenge_participation in all_participations:
        if not UserAcceptsTeamInChallenge.objects.filter(team=challenge_participation, user=request.user).exists():
            context['invitations'].append(challenge_participation)
        else:
            context['accepted_participations'].append(challenge_participation.team)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            context['submissions'] = Paginator(
                TeamSubmission.objects.filter(team=participation_id).order_by('-id'),
                10
            ).page(page)
    else:
        form = SubmissionForm()
        form.fields['team'].queryset = TeamParticipatesChallenge.objects.filter(
            team__in=context['accepted_participations']
        )
        if participation is not None:
            form.initial['team'] = participation
            form.fields['team'].empty_label = None

    context['form'] = form
    context['form_challenge'] = ChallengeATeamForm()
    if participation is not None:
        context['challenge_teams'] = [team_part.team for team_part in
                                      TeamParticipatesChallenge.objects.filter(challenge=participation.challenge)]
        context.update({
            'participation_id': participation_id,
            'battle_history': Match.objects.all()  # TODO : ok it
        })
    return render(request, 'accounts/panel.html', context)


@login_required
def set_final_submission(request, submission_id):
    submission = TeamSubmission.objects.get(id=submission_id)
    if submission.team.team.participants.filter(
            user=request.user).count() == 0 or not submission.team.challenge.is_submission_open:
        return Http404()
    submission.set_final()
    data = {'success': True, 'submission_id': submission_id}
    return HttpResponse(json.dumps(data))


@login_required
def accept_participation(request, participation_id):
    team = get_object_or_404(TeamParticipatesChallenge,
                             id=participation_id,
                             team__participants__user=request.user)
    UserAcceptsTeamInChallenge.objects.get_or_create(team=team, user=request.user)
    TeamParticipatesChallenge.objects.filter(
        challenge=team.challenge,
        team__participants__user=request.user,
    ).exclude(id=team.id).delete()
    return redirect('accounts:panel', participation_id)


@login_required
def reject_participation(request, participation_id):
    team = get_object_or_404(TeamParticipatesChallenge,
                             id=participation_id,
                             team__participants__user=request.user)
    team.delete()
    logger.info("User {}(#{}) rejected the request for team {}(#{})".format(
        request.user,
        request.user.id,
        team,
        team.id
    ))
    return redirect('accounts:panel')


@login_required()
def create_team(request, challenge_id):
    if UserAcceptsTeamInChallenge.objects.filter(
            team__challenge_id=challenge_id,
            team__team__participants__user=request.user
    ).exists():
        return redirect('accounts:panel')
    if request.method == 'POST':
        form = CreateTeamForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:success_create_team')
    else:
        form = CreateTeamForm(user=request.user, initial={'challenge_id': challenge_id})
    already_participated_users_accepts = UserAcceptsTeamInChallenge.objects.filter(team__challenge_id=challenge_id)
    already_participated_usernames = [accept.user.username for accept in already_participated_users_accepts]
    return render(request, 'accounts/create_team.html', {
        'form': form,
        'users': User.objects.exclude(username__exact=request.user.username).exclude(
            username__in=already_participated_usernames).exclude(is_active=False),
        'username': request.user.username
    })


@login_required()
def add_participation(request, participation_id):
    acceptance = get_object_or_404(UserAcceptsTeamInChallenge,
                                   team_id=participation_id,
                                   user=request.user)
    if request.method == 'POST':
        form = AddParticipationForm(request.user, acceptance.team.challenge, acceptance.team.team, request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:success_create_team')
    else:
        form = AddParticipationForm(user=request.user, team=acceptance.team.team, challenge=acceptance.team.challenge)
    already_participated_users_accepts = UserAcceptsTeamInChallenge.objects.filter(
        team__challenge_id=acceptance.team.challenge.id)
    already_participated_usernames = [accept.user.username for accept in already_participated_users_accepts]
    return render(request, 'accounts/add_member.html', {
        'team': acceptance.team.team,
        'form': form,
        'users': User.objects.exclude(username__exact=request.user.username).exclude(
            username__in=already_participated_usernames).exclude(is_active=False),
        'username': request.user.username
    })


@login_required
def success_create_team(request):
    return render(request, 'accounts/success_create_team.html',
                  {
                      'last_participation_id': TeamParticipatesChallenge.objects.last().id
                  })


def cancel_participation_request(request, participation_id, user_id):
    accepted = get_object_or_404(UserAcceptsTeamInChallenge,
                                 team_id=participation_id,
                                 user=request.user)

    if UserAcceptsTeamInChallenge.objects.filter(
            user_id=user_id,
            team__team=accepted.team.team
    ).exists():
        return redirect('accounts:panel', participation_id)

    participation_request = get_object_or_404(UserParticipatesOnTeam,
                                              team=accepted.team.team,
                                              user_id=user_id)
    participation_request.delete()
    return redirect('accounts:panel', participation_id)


@login_required()
def challenge_a_team(request, participation_id):
    # TODO : add time limit for challenging a team
    #    return HttpResponse(request.POST['battle_team'])

    if participation_id is not None:
        try:
            participation = TeamParticipatesChallenge.objects.get(
                id=participation_id,
                team__participants__user=request.user
            )
        except TeamParticipatesChallenge.DoesNotExist:
            return redirect('accounts:panel')
    else:
        return redirect(reverse('accounts:panel', args=[participation_id]))

    try:
        challenge = participation.challenge

        team1 = participation.team

        competition = Competition.objects.filter(challenge=challenge, type='friendly').first()

        team2_ = Team.objects.filter(id=request.POST['battle_team']).first()
        team2 = TeamParticipatesChallenge.objects.filter(team=team2_, challenge=challenge).first()

        part1 = Participant()
        part1.depend = participation
        part1.submission = participation.get_final_submission()
        part1.save()

        part2 = Participant()
        part2.depend = team2
        part2.submission = team2.get_final_submission()
        part2.save()

        match = Match(part1=part1, part2=part2, competition=competition)
        match.save()

        competition_map = Map.objects.filter(id=request.POST['battle_team_maps']).first()

        single_match = SingleMatch(match=match, map=competition_map)
        single_match.save()

        single_match.handle()

    except Exception as e:
        logger.error("Team failed to submit : " + str(e))

    # single_match.
    return redirect(reverse('accounts:panel', args=[participation_id]))


def team_required_and_finalized():
    raise NotImplemented
    pass
