from django.urls import reverse
from django.utils.translation import ugettext as _


def menu(request):
    return {
        'ai': {
            'navbar': {
                _('Home'): {
                    'address': reverse('intro:index')
                },
                _('Blog'): {
                    'address': reverse('zinnia:entry_archive_index')
                }
            },
            'sidebar': {

            }
        }
    }
