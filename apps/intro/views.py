from django.shortcuts import render


def index(request):
    return render(request, 'intro/index.html', {
        'no_sidebar': True,
        'ai': {
            'navbar': {
                _('Introduce'): {
                    'address': '#section-intro'
                },
                _('Prize'): {
                    'address': '#section-prizes'
                },
                _('History'): {
                    'address': '#section-history'
                },
                _('Schedule'): {
                    'address': '#section-schedule'
                },
                _('Organizer'): {
                    'address': '#section-organizer'
                }
            }
        }
    })


def faq(request):
    return render(request, 'intro/faq.html')
