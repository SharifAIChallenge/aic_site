from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from apps.accounts.forms.panel import SubmissionForm, ChallengeATeamForm
from apps.game.models import TeamSubmission, Match, TeamParticipatesChallenge
from django.core.paginator import Paginator
from django.db.models import Q
from apps.game.models.challenge import Challenge, UserAcceptsTeamInChallenge


@login_required
def get_team_pc(request):
    if request.user.profile.panel_active_teampc:
        return request.user.profile.panel_active_teampc
    try:
        pc = TeamParticipatesChallenge.objects.filter(team__participants__user=request.user).order_by('-id').first()
        request.user.profile.panel_active_teampc = pc
        request.user.profile.save()
        return pc
    except TeamParticipatesChallenge.DoesNotExist:
        return None


@login_required
def get_shared_context(request):
    context = {
        'challenges': Challenge.objects.all(),
        'invitations': [],
        'accepted_participations': []
    }

    all_participations = TeamParticipatesChallenge.objects.filter(
        team__participants__user=request.user
    )
    for challenge_participation in all_participations:
        if UserAcceptsTeamInChallenge.objects.filter(team=challenge_participation, user=request.user).exists():
            context['accepted_participations'].append(challenge_participation.team)

    context['user_pcs'] = []
    for tpc in TeamParticipatesChallenge.objects.filter(team__in=context['accepted_participations']):
        context['user_pcs'].append(tpc)

    context['menu_items'] = [
        {'name': 'team_management', 'link': reverse('accounts:panel_team_management'), 'text': _('Team Status')},
        {'name': 'submissions', 'link': reverse('accounts:panel_submissions'), 'text': _('Submissions')},
        {'name': 'battle_history', 'link': reverse('accounts:panel_battle_history'), 'text': _('Battle history')},
        {'name': 'friendly_scoreboard', 'link': reverse('game:scoreboard', args=[2]), 'text': _('Friendly Scoreboard')}
    ]

    return context


@login_required
def change_team_pc(request, team_pc):
    try:
        new_pc = TeamParticipatesChallenge.objects.get(team__participants__user=request.user, id=team_pc)
        request.user.profile.panel_active_teampc = new_pc
        request.user.profile.save()
    except TeamParticipatesChallenge.DoesNotExist:
        raise Http404
    return redirect('accounts:panel_team_management')


@login_required
def submissions(request):
    team_pc = get_team_pc(request)
    context = get_shared_context(request)

    for item in context['menu_items']:
        if item['name'] == 'submissions':
            item['active'] = True

    page = request.GET.get('page', 1)
    context.update({
        'page': page,
        'participation': team_pc,
    })

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['team'] == team_pc:
            form.save()
            return redirect('accounts:panel_submissions')
    else:
        form = SubmissionForm()

    context['submissions'] = Paginator(
        TeamSubmission.objects.filter(team_id=team_pc.id).order_by('-id'),
        5
    ).page(page)

    if team_pc is not None:
        form.initial['team'] = team_pc
        form.fields['team'].empty_label = None
        form.fields['file'].widget.attrs['accept'] = '.zip'

    context['form'] = form
    context['team_pc'] = team_pc
    return render(request, 'accounts/panel/submissions.html', context)


@login_required
def team_management(request, participation_id=None):
    team_pc = get_team_pc(request)
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'team_management':
            item['active'] = True
    context.update({
        'participation': team_pc,
        'participation_members': [
            (
                user_part.user,
                not UserAcceptsTeamInChallenge.objects.filter(
                    user=user_part.user,
                    team__team=team_pc.team
                ).exists()
            )
            for user_part in team_pc.team.participants.all()] if team_pc else [],
        'challenges': Challenge.objects.all(),
        'invitations': [],
        'accepted_participations': []
    })

    all_participations = TeamParticipatesChallenge.objects.filter(
        team__participants__user=request.user
    )
    if all_participations.count() > 0 and team_pc is None:
        return redirect('accounts:panel', all_participations.first().id)
    for challenge_participation in all_participations:
        if not UserAcceptsTeamInChallenge.objects.filter(team=challenge_participation, user=request.user).exists():
            context['invitations'].append(challenge_participation)
        else:
            context['accepted_participations'].append(challenge_participation.team)
    return render(request, 'accounts/panel/team_management.html', context)


@login_required
def battle_history(request):
    team_pc = get_team_pc(request)
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'battle_history':
            item['active'] = True

    battles_page = request.GET.get('battles_page', 1)

    participation = team_pc
    participation_id = team_pc.id
    if participation is not None and participation.challenge.competitions.filter(type='friendly').exists():
        context['form_challenge'] = ChallengeATeamForm(user=request.user, participation=participation)
        context['friendly_competition'] = participation.challenge.competitions.get(type='friendly')
        if participation is not None:
            context['challenge_teams'] = [team_part.team for team_part in
                                          TeamParticipatesChallenge.objects.filter(challenge=participation.challenge)]
            context.update({
                'participation': participation,
                'participation_id': participation_id,
                'battles_page': battles_page,
                'battle_history': Paginator(Match.objects.filter(Q(part1__object_id=participation_id) |
                                                                 Q(part2__object_id=participation_id)).order_by('-id'),
                                            5).page(battles_page)
            })
    return render(request, 'accounts/panel/battle_history.html', context)
