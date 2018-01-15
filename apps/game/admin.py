from django.contrib import admin

# Register your models here.
from apps.game.models import Challenge, Game, Competition, Participant, Match, TeamParticipatesChallenge
from apps.game.models import TeamSubmission


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
    fields = ['name']

    inlines = [ChallengeInline]

    list_display = ('id', 'name')
    #list_filter = []

    #search_fields = []

class ChallengeAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Challenge', {'fields': ['title', 'description', 'registration_open']}),
        ('Challenge Information', {'fields': ['game', 'team_size', 'entrance_price']}),
        ('Challenge Timing', {'fields': ['registration_start_time', 'registration_end_time',
                                         'start_time', 'end_time']})
        ]
    inlines = [CompetitionInline,TeamParticipatesChallengeInline]

    list_display = ('id', 'title')
    list_filter = ['game', 'registration_open']

    #search_fields = []

class CompetitionAdmin(admin.ModelAdmin):
    fields = ['name', 'type']

    inlines = [MatchInline]

    list_display = ('name', 'type')
    list_filter = ['type']

    #search_fields = []

class MatchAdmin(admin.ModelAdmin):
    fields = ['competition', 'part1', 'part2', 'done']

    list_display = ('id', 'competition', 'part1', 'part2')
    list_filter = ['competition', 'done']

    #search_fields = []

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
#admin.site.register(TeamParticipatesChallenge, TeamParticipatesChallengeAdmin)
# admin.site.register(TeamSubmission, TeamSubmissionAdmin)

admin.site.register(Competition, CompetitionAdmin)
# admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Match, MatchAdmin)

