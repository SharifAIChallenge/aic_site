from django.urls import reverse
from django.utils.translation import ugettext as _


def menu(request):
    print("sssssasd" + str(request.build_absolute_uri(reverse('intro:index'))))
    context = {
        'ai': {
            'navbar': {
                _('Home'): {
                    'dropdown': {
                        _('Introduction'): reverse('intro:index') + '#section-intro',
                        _('Prize'): reverse('intro:index') + '#section-prizes',
                        _('History'): reverse('intro:index') + "#section-history",
                        _('Schedule'): reverse('intro:index') + '#section-schedule',
                        _('FAQ'): reverse('intro:faq'),
                        _('Contact Us'): reverse('intro:index') + '#section-organizer'
                    }
                }
            }
        }
    }

    return context
