from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from aic_site.settings.base import UPLOAD_MAP_TIME_DELTA
from apps.accounts.forms.panel import SubmissionForm, ChallengeATeamForm
from apps.billing.decorators import payment_required
from apps.game.models import TeamSubmission, Match, Team, TeamParticipatesChallenge, Competition, SingleMatch
from apps.game.forms import MapForm
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
      # {'name': 'team_profile', 'link': reverse('accounts:team_profile'), 'text': _('Team Profile')},
      {'name': 'submissions', 'link': reverse('accounts:panel_submissions'), 'text': _('Submissions')},
      # {'name': 'battle_history', 'link': reverse('accounts:panel_battle_history'), 'text': _('Battle history')},
      # {'name': 'upload_map', 'link': reverse('accounts:upload_map'), 'text': _('Upload Map')},
      # {'name': 'rating', 'link': reverse('a ccounts:rating'), 'text': _('Rating')}
    ]

    if request.user.profile:
        if request.user.profile.panel_active_teampc:
            if request.user.profile.panel_active_teampc.should_pay and not request.user.profile.panel_active_teampc.has_paid:
                context['payment'] = request.user.profile.panel_active_teampc
            # if request.user.profile.panel_active_teampc.challenge.competitions.filter(
            #         type='friendly'
            # ).exists():
            #     context['menu_items'].append(
            #         {
            #             'name': 'friendly_scoreboard',
            #             'link': reverse('game:scoreboard', args=[
            #                 request.user.profile.panel_active_teampc.challenge.competitions.get(
            #                     type='friendly'
            #                 ).id
            #             ]),
            #             'text': _('Friendly Scoreboard')
            #         }
            #     )
            #
            # if request.user.profile.panel_active_teampc.challenge.competitions.filter(
            #         type='league'
            # ).exists():
            #     context['menu_items'].append(
            #         {
            #             'name': 'friendly_scoreboard',
            #             'link': reverse('game:league_scoreboard', args=[
            #                 request.user.profile.panel_active_teampc.challenge.id
            #             ]),
            #             'text': _('League')
            #         }
            #     )

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


@payment_required
@login_required
def submissions(request):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)

    for item in context['menu_items']:
        if item['name'] == 'submissions':
            item['active'] = True

    context.update({
        'participation': team_pc,
        'participation_id': team_pc.id,
    })

    page = request.GET.get('page', 1)

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


def redirect_to_somewhere_better(request):
    if Challenge.objects.filter(is_submission_open=True).exists():
        return HttpResponseRedirect(
            reverse(
                'accounts:create_team',
                args=[Challenge.objects.get(is_submission_open=True).id]
            )
        )
    else:
        return HttpResponseRedirect(reverse(
            'intro:index'
        ))


@login_required
def team_management(request, participation_id=None):
    if participation_id is not None:
        return change_team_pc(request, participation_id)
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'team_management':
            item['active'] = True
    context.update({
        'participation': team_pc,
        'participation_id': team_pc.id,
        'participation_members': [
            (
                user_part.user,
                not UserAcceptsTeamInChallenge.objects.filter(
                    user=user_part.user,
                    team=team_pc
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


@payment_required
@login_required
def battle_history(request):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'battle_history':
            item['active'] = True

    battles_page = request.GET.get('battles_page', 1)

    participation = team_pc
    if participation:
        participation_id = team_pc.id
        context.update({
            'participation': participation,
            'participation_id': participation_id,
        })

    if participation is not None and participation.challenge.competitions.filter(type='friendly').exists():
        context['form_challenge'] = ChallengeATeamForm(user=request.user, participation=participation)
        context['friendly_competition'] = participation.challenge.competitions.get(type='friendly')
        if participation is not None:
            context['challenge_teams'] = [team_part.team for team_part in
                                          TeamParticipatesChallenge.objects.filter(challenge=participation.challenge)]
            context.update({
                'battles_page': battles_page,
                'battle_history': Paginator(
                    Match.objects.filter(
                        Q(part1__object_id=participation_id) |
                        Q(part2__object_id=participation_id)).order_by('-id').filter(
                        competition__type='friendly'
                    ),
                    5).page(battles_page)
            })
    return render(request, 'accounts/panel/battle_history.html', context)


@payment_required
@login_required
def upload_map(request):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)

    for item in context['menu_items']:
        if item['name'] == 'upload_map':
            item['active'] = True

    page = request.GET.get('page', 1)
    context.update({
        'page': page,
        'participation': team_pc,
        'participation_id': team_pc.id,
        'timedelta': UPLOAD_MAP_TIME_DELTA,
    })

    if request.method=='POST':
        form = MapForm(request.POST, request.FILES)
        print(form)
        if form.is_valid(get_team_pc(request)):
            map = form.save(commit=False)
            map.team = team_pc
            map.save()
            map.file.compress(async=False)
            map.save()
            print(map.file)
            context.update({
                'form': form
            })
            return render(request, 'accounts/panel/valid_upload.html', context)
        else:
            print(form.errors)
            context.update({
                'form':form
             })
            return render(request, 'accounts/panel/upload_map.html', context)
    elif request.method=='GET':
        form = MapForm()
        context.update({
            'form': form
        })
        return render(request, 'accounts/panel/upload_map.html', context)


@payment_required
@login_required
def rating(request):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)

    for item in context['menu_items']:
        if item['name'] == 'rating':
            item['active'] = True

    context.update({
        'participation': team_pc,
        'participation_id': team_pc.id,
    })

    all_teams = sorted(list(Team.objects.all()), key=lambda x: -x.rate)
    paginator = Paginator(all_teams, 50)
    page = request.GET.get('page', 1)
    teams = paginator.page(page)
    current_team = team_pc.team

    context.update( {
        'teams': teams,
        'rank': all_teams.index(current_team) + 1,
        'current_team': current_team
    } )

    return render(request, 'accounts/panel/rating.html', context )

@payment_required
@login_required
def team_profile(request):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)


    for item in context['menu_items']:
        if item['name'] == 'team_profile':
            item['active'] = True
    context.update({
        'participation': team_pc,
        'participation_id': team_pc.id,
    })

    tid = request.GET.get('tid', team_pc.team.id)
    team = Team.objects.get(id=tid)

    context.update( {'team': team })

    return render(request, 'accounts/panel/team_profile.html', context )

@payment_required
@login_required
def accept_friendly(request, sm_id):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)

    single_match = SingleMatch.objects.get(id=sm_id)

    if single_match.match.part2.submission and single_match.match.part2.submission.team == team_pc:
        single_match.status = 'waiting'
        single_match.save()
        single_match.handle()
        return redirect('accounts:panel_battle_history')

    return redirect('accounts:panel_battle_history')


@payment_required
@login_required
def reject_friendly(request, sm_id):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)

    single_match = SingleMatch.objects.get(id=sm_id)

    if single_match.match.part2.submission and single_match.match.part2.submission.team == team_pc:
        single_match.status = 'rejected'
        single_match.save()

    return redirect('accounts:panel_battle_history')
