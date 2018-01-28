from django.urls import reverse
from django.utils.translation import ugettext as _


def menu(request):
    context = {
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
                # (_('Contact Us'), {
                #     'address': '#section-organizer'
                # })
            ],
            'sidebar': {

            }
        }
    }

    if request.user.is_authenticated():
        context['ai']['sidebar'].update({
            _('Panel'): {
                'address': reverse('accounts:panel')
            },
            _('Create Team'): {
                'address': reverse('accounts:panel')
            },
        })

    return context
