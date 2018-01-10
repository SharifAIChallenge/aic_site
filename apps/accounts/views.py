from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.views.generic import FormView, CreateView
from apps.accounts.forms.forms_team import CreateTeamForm
from apps.accounts.models import Team, UserParticipatesOnTeam


def create_team(request):
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            form.save()
            team_name = form.cleaned_data.get('team_name')
            if not Team.objects.filter(name__exact=team_name).exists():
                team = Team(name=team_name)
                team.save()
                team_user = UserParticipatesOnTeam(team=team, user=request.user)
                team_user.save()
    else:
        form = CreateTeamForm()
    return render(request, 'accounts/team.html',
                  {'form': form}, {'team_user': UserParticipatesOnTeam.objects.filter(team__name__exact='team1')})

#def add_member(request):
