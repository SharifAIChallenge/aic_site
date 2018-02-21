import json
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from apps.accounts.forms.panel import ChallengeATeamForm
from apps.accounts.forms.team_forms import CreateTeamForm, AddParticipationForm
from apps.accounts.models import UserParticipatesOnTeam
from apps.accounts.views import panel
from apps.game.models.challenge import TeamParticipatesChallenge, TeamSubmission
from apps.game.models.challenge import UserAcceptsTeamInChallenge

logger = logging.getLogger(__name__)


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
    return render(request, 'accounts/teams/create_team.html', {
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
    return render(request, 'accounts/teams/add_member.html', {
        'team': acceptance.team.team,
        'form': form,
        'users': User.objects.exclude(username__exact=request.user.username).exclude(
            username__in=already_participated_usernames).exclude(is_active=False),
        'username': request.user.username
    })


@login_required
def success_create_team(request):
    return render(request, 'accounts/teams/success_create_team.html',
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


@login_required
def challenge_a_team(request, participation_id):
    participation = panel.get_team_pc(request)
    if participation is None:
        return redirect(reverse('accounts:panel_team_management'))
    else:
        participation_id = participation.id
    # if participation_id is not None:
    #     try:
    #         participation = TeamParticipatesChallenge.objects.get(
    #             id=participation_id,
    #             team__participants__user=request.user
    #         )
    #     except TeamParticipatesChallenge.DoesNotExist:
    #         return redirect('accounts:panel')
    # else:
    #     return redirect(reverse('accounts:panel', args=[participation_id]))

    if request.method == 'POST':
        form = ChallengeATeamForm(data=request.POST, user=request.user, participation=participation)
        if form.is_valid():
            form.save()
        return render(request, 'accounts/panel/friendly_result.html', {'form': form})
    return redirect(reverse('accounts:panel', args=[participation_id]))
