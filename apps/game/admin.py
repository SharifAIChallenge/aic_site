from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.game.models import Challenge, Game, Competition, Participant, Match, TeamParticipatesChallenge, Map

from apps.game.models.challenge import UserAcceptsTeamInChallenge


class ChallengeInline(admin.StackedInline):
    model = Challenge
    extra = 1
    show_change_link = True


class CompetitionInline(admin.StackedInline):
    model = Competition
    extra = 1
    show_change_link = True


class TeamParticipatesChallengeInline(admin.StackedInline):
    model = TeamParticipatesChallenge
    extra = 1
    show_change_link = True


class MatchInline(admin.StackedInline):
    model = Match
    extra = 1
    show_change_link = True


class GameAdmin(admin.ModelAdmin):
    fields = ['name', 'infra_token']

    inlines = [ChallengeInline]

    list_display = ('id', 'name')
    # list_filter = []

    # search_fields = []


class ChallengeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Challenge', {'fields': ['title', 'description', 'registration_open']}),
        ('Challenge Information', {'fields': ['game', 'team_size', 'entrance_price']}),
        ('Challenge Timing', {'fields': ['registration_start_time', 'registration_end_time',
                                         'start_time', 'end_time']})
    ]
    inlines = [CompetitionInline, TeamParticipatesChallengeInline]

    list_display = ('id', 'title')
    list_filter = ['game', 'registration_open']

    # search_fields = []


class CompetitionAdmin(admin.ModelAdmin):
    fields = ['name', 'type', 'challenge']

    inlines = [MatchInline]
    list_display = ('name', 'type')
    list_filter = ['type']


# search_fields = []

class MatchAdmin(admin.ModelAdmin):
    fields = ['competition', 'part1', 'part2']

    list_display = ('id', 'competition', 'part1', 'part2')
    list_filter = ['competition']

    # search_fields = []


class TeamParticipatesChallengeAdmin(admin.ModelAdmin):
    fields = ['team', 'challenge']

    actions = ['create_new_league', 'create_new_double_elimination']
    list_display = ('id', 'team', 'challenge')
    list_filter = ['challenge']

    def create_new_league(self, request, queryset):
        teams = list(queryset)

        if len(teams) < 1:
            from django.contrib import messages
            messages.error(request, _('no selected teams!'))
            return

        first_challenge = teams[0].challenge
        for team in teams:
            if team.challenge != first_challenge:
                from django.contrib import messages
                messages.error(request, _('Only teams from one challenge!'))
                return
        new_competition = Competition(challenge=first_challenge, name=str(len(first_challenge.competitions.all()) + 1),
                                      type='league')
        new_competition.save()
        new_competition.create_new_league(
            [team.team for team in teams]
        )

    def create_new_double_elimination(self, request, queryset):
        teams = list(queryset)
        if len(teams) < 1:
            from django.contrib import messages
            messages.error(request, _('no selected teams!'))
            return

        first_challenge = teams[0].challenge
        for team in teams:
            if team.challenge != first_challenge:
                from django.contrib import messages
                messages.error(request, _('Only teams from one challenge!'))
                return
        new_competition = Competition(challenge=first_challenge, name=str(len(first_challenge.competitions.all()) + 1),
                                      type='double')
        new_competition.save()
        new_competition.create_new_double_elimination(
            [team.team for team in teams]
        )



        # search_fields = []


# class TeamSubmissionAdmin(admin.ModelAdmin):
#     fields = ['team', 'file', 'language', 'is_final', 'time', 'infra_compile_message']
#
#     inlines = [Inline]
#
#     list_display = ('id', 'title')
#     list_filter = ['game', 'registraion_open']
#
#     # search_fields = []


admin.site.register(Game, GameAdmin)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(TeamParticipatesChallenge, TeamParticipatesChallengeAdmin)
# admin.site.register(TeamSubmission, TeamSubmissionAdmin)

admin.site.register(Competition, CompetitionAdmin)
# admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Match, MatchAdmin)

admin.site.register(UserAcceptsTeamInChallenge)
admin.site.register(Participant)


class MapAdmin(admin.ModelAdmin):
    fields = ['name', 'file', 'token']
    readonly_fields = ['token']


admin.site.register(Map, MapAdmin)
