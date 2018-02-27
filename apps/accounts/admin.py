from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin

from apps.accounts.models import Profile, Team, UserParticipatesOnTeam


class UserInline(admin.StackedInline):
    model = UserParticipatesOnTeam
    extra = 0
    show_change_link = True


class TeamAdmin(admin.ModelAdmin):
    fields = ['name']

    inlines = [UserInline]

    list_display = ('id', 'name')
    # list_filter = []

    # search_fields = []


admin.site.register(Team, TeamAdmin)


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        fields = [
            'user__username',
            'user__first_name',
            'user__last_name',
            'user__email',
            'phone_number',
            'organization',
        ]


class ProfileAdmin(ImportExportModelAdmin):
    list_filter = ['user__teams__team__challenges__challenge']
    resource_class = ProfileResource


admin.site.register(Profile, ProfileAdmin)
