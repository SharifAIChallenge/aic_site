from django.urls import reverse
from django.utils.translation import ugettext as _


def menu(request):
    context = {
        'ai': {
            'navbar': {
                _('Home'): {
                    'address': reverse('intro:index')
                },
                _('Blog'): {
                    'address': reverse('zinnia:entry_archive_index')
                },
                _('FAQ'): {
                    'address': reverse('intro:faq')
                }
            },
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
