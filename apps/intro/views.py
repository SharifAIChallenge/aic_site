from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


def index(request):
    return render(request, 'intro/index.html', {
        'no_sidebar': True,
    })


def faq(request):
    return render(request, 'intro/faq.html')
