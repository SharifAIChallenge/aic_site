from django.shortcuts import render
from apps.accounts.models import Team
from apps.accounts.models import User


def index(request):

    return render(request, 'intro/index.html', {'teams': Team.objects, 'users': User.objects},)
