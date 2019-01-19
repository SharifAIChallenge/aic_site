from django.shortcuts import render, redirect

# Create your views here.
from apps.modir.models import URLShortner


def redirect_shortened_url(request, shortened):
    url = URLShortner.objects.get(shortened=shortened).main
    print(url)
    return redirect(url)
