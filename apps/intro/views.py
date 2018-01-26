from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


def index(request):
    return render(request, 'intro/index.html', {
        'no_sidebar': True,
        'ai': {
            'navbar': [
                (_('Introduction'), {
                    'address': '#section-intro'
                }),
                (_('Prize'), {
                    'address': '#section-prizes'
                }),
                (_('History'), {
                    'address': '#section-history'
                }),
                (_('Schedule'), {
                    'address': '#section-schedule'
                }),
                (_('Contact Us'), {
                    'address': '#section-organizer'
                })
            ]
        }
    })


def faq(request):
    return render(request, 'intro/faq.html')
