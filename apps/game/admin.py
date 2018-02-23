from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.game.models import Challenge, Game, Competition, Participant, Match, TeamParticipatesChallenge, Map, \
    SingleMatch, \
    TeamSubmission

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
    raw_id_fields = ['part1', 'part2']
    extra = 1
    show_change_link = True


class MapInline(admin.StackedInline):
    model = Competition.maps.through
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
                                         'start_time', 'end_time', 'is_submission_open']})
    ]
    inlines = [CompetitionInline, TeamParticipatesChallengeInline]

    list_display = ('id', 'title')
    list_filter = ['game', 'registration_open']

    # search_fields = []


class CompetitionAdmin(admin.ModelAdmin):
    fields = ['name', 'type', 'challenge']

    inlines = [MatchInline, MapInline]
    list_display = ('name', 'type')
    list_filter = ['type']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class StatusListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, MatchAdmin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('running', _('running')),
            ('failed', _('failed')),
            ('done', _('done')),
            ('waiting', _('waiting')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'running':
            match_pks = [obj.pk for obj in queryset if obj.status == 'running']
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'failed':
            match_pks = [obj.pk for obj in queryset if obj.status == 'failed']
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'done':
            match_pks = [obj.pk for obj in queryset if obj.status == 'done']
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'waiting':
            match_pks = [obj.pk for obj in queryset if obj.status == 'waiting']
            return queryset.filter(pk__in=match_pks)


class IsReadyToRunListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('is ready')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is ready'

    def lookups(self, request, MatchAdmin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('True', _('True')),
            ('False', _('False')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'True':
            match_pks = [obj.pk for obj in queryset if obj.is_ready_to_run() == True]
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'False':
            match_pks = [obj.pk for obj in queryset if obj.is_ready_to_run() == False]
            return queryset.filter(pk__in=match_pks)


class MatchAdmin(admin.ModelAdmin):
    fields = ['competition', 'part1', 'part2']
    raw_id_fields = ['part1', 'part2']

    actions = ['run_selected_matches']
    list_display = ('id', 'competition', 'part1', 'part2', 'status', 'is_ready_to_run')
    list_filter = ['competition', StatusListFilter, IsReadyToRunListFilter]

    # search_fields = []
    def run_selected_matches(self, request, queryset):
        matches = list(queryset)

        if len(matches) < 1:
            from django.contrib import messages
            messages.error(request, _('no selected matches!'))
            return

        single_matches = []
        for match in matches:
            from django.contrib import messages

            if not match.is_ready_to_run():
                messages.error(request, _('one of selected matches is not ready!'))
                return

            if match.status == 'done':
                messages.error(request, _('one of selected matches is done!'))
                return

        for match in matches:
            match.ensure_submissions()
            match.handle()
            # for single_match in match.single_matches.all():
            #     single_matches.append(single_match)

        # from apps.game import functions
        # matches_details = functions.run_matches(single_matches)
        # print(matches_details)
        # cnt = 0
        # for match in matches:
        #     for single_match in match.single_matches.all():
        #         if matches_details[cnt]['success'] == True:
        #             single_match.status = 'running'
        #             single_match.save()
        #         cnt += 1
        # for match in matches:
        #     for single_match in match.single_matches.all():
        #         print(single_match.status)
        #     print(match.status)


class HasSubmittedListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('submitted')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'submitted'

    def lookups(self, request, team_pc_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('True', _('True')),
            ('False', _('False')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'True':
            match_pks = [obj.pk for obj in queryset if obj.has_submitted() == True]
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'False':
            match_pks = [obj.pk for obj in queryset if obj.has_submitted() == False]
            return queryset.filter(pk__in=match_pks)


class TeamParticipatesChallengeAdmin(admin.ModelAdmin):
    fields = ['team', 'challenge']

    actions = ['create_new_league', 'create_new_double_elimination']
    list_display = ('id', 'team', 'challenge')
    list_filter = ['challenge', HasSubmittedListFilter]

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
            [team.team for team in teams], 1
        )
        new_competition.save()

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
        new_competition.save()

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
    fields = ['name', 'file', 'token', 'competitions']
    readonly_fields = ['token']


admin.site.register(Map, MapAdmin)
admin.site.register(SingleMatch)
admin.site.register(TeamSubmission)
