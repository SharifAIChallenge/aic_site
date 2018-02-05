from django.urls import reverse
from django.utils.translation import ugettext as _


def menu(request):
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
                        _('Blog and Q&A'): '/blog',
                        _('Contact Us'): reverse('intro:index') + '#section-organizer',
                    }
                }
            },
            'sidebar': {
                _('Home'): {
                    'dropdown': {
                        _('Introduction'): reverse('intro:index') + '#section-intro',
                        _('Prize'): reverse('intro:index') + '#section-prizes',
                        _('History'): reverse('intro:index') + "#section-history",
                        _('Schedule'): reverse('intro:index') + '#section-schedule',
                        _('Contact Us'): reverse('intro:index') + '#section-organizer'
                    }
                },
                _('Blog'): {
                    'dropdown': {
                        _('FAQ'): reverse('intro:faq'),
                        _('Blog and Q&A'): '/blog',
                    }
                },
                _('Game'): {
                    'dropdown': {
                        _('Panel'): reverse('accounts:panel'),
                        _('Game Viewer'): '/static/game_graphics/game_viewer/index.html',
                        _('Map Maker'): '/static/game_graphics/map_maker/index.html',
                    }
                },
                _('Account'): {
                    'dropdown': {
                        _('Logout'): reverse('accounts:logout'),
                    }
                }
            }
        }
    }

    return context
