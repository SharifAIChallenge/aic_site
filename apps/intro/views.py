from django.shortcuts import render


def index(request):
    return render(request, 'intro/index.html', {'stats': {
        'teams_count': 97,
        'submissions_count': 418
    }})
