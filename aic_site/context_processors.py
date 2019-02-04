from django.urls import reverse
from django.utils.translation import ugettext as _

from apps.game.models import Competition


def menu(request):
    context = {
        'ai': {
            'navbar': {
                _('Home'): {
                    'dropdown': {
                        _('Main Page'): reverse('intro:index'),
                        _('Introduction'): reverse('intro:index') + '#section-intro',
                        _('Prize'): reverse('intro:index') + '#section-prizes',
                        # _('Schedule'): reverse('intro:index') + '#section-schedule',
                        # _('FAQ'): reverse('intro:index') + "#section-faq",
                        # _('Contact Us'): reverse('intro:index') + '#section-organizer',
                    }
                },

                _('Blog'): reverse('zinnia:entry_archive_index'),

                # _('Contact Us'): reverse('intro:index') + '#section-organizer',
                # _('Access'): {
                #     'dropdown': {
                #         _('Panel'): reverse('accounts:panel'),
                #         _('Resources'): 'https://aichallenge.sharif.edu/blog/2018/02/05/Server-Client-MapMaker/',
                #         _('Blog and Q&A'): '/blog',
                #         _('Staff'): '/staff',
                #     }
                # },
            },
            # 'sidebar': {
            #     _('Home'): {
            #         'dropdown': {
            #             _('Introduction'): reverse('intro:index') + '#section-intro',
            #             _('Prize'): reverse('intro:index') + '#section-prizes',
            #             _('History'): reverse('intro:index') + "#section-history",
            #             _('Schedule'): reverse('intro:index') + '#section-schedule',
            #             _('Contact Us'): reverse('intro:index') + '#section-organizer'
            #         }
            #     },
            #     _('Blog'): {
            #         'dropdown': {
            #             _('FAQ'): reverse('intro:faq'),
            #             _('Blog and Q&A'): '/blog',
            #         }
            #     },
            #     _('Game'): {
            #         'dropdown': {
            #             _('Panel'): reverse('accounts:panel'),
            #             _('Game Viewer'): '/game/game_viewer',
            #             _('Map Maker'): '/game/map_maker',
            #         }
            #     },
            #     _('Account'): {
            #         'dropdown': {}
            #     },
            #     _('Scoreboard'): {
            #         'dropdown': {},
            #     },
            # }
        }
    }

    # if request.user.is_authenticated():
    #     context['ai']['sidebar'][_('Account')]['dropdown'][_('Logout')] = reverse('accounts:logout')
    # else:
    #     context['ai']['sidebar'][_('Account')]['dropdown'][_('Login')] = reverse('accounts:login')

    # friendly_competitions = Competition.objects.filter(type='friendly')
    # for friendly_competition in friendly_competitions:
    #     context['ai']['sidebar'][_('Scoreboard')]['dropdown'][friendly_competition.name] = reverse('game:scoreboard', args=[friendly_competition.id])
    #
    # if request.user.is_authenticated:
    #     if request.user.profile.panel_active_teampc:
    #         if request.user.profile.panel_active_teampc.challenge.competitions.filter(
    #             type='league'
    #         ).exists():
    #             context['ai']['sidebar'][_('Scoreboard')]['dropdown'][_('League')] = reverse('game:league_scoreboard', args=[
    #                         request.user.profile.panel_active_teampc.challenge.id
    #                     ])

    return context
