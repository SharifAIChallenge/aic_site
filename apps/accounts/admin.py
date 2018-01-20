from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.
from apps.accounts.models import Profile,Team, UserParticipatesOnTeam


class UserInline(admin.StackedInline):
    model = UserParticipatesOnTeam
    extra = 0
    show_change_link = True


class TeamAdmin(admin.ModelAdmin):
    fields = ['name']

    inlines = [UserInline]

    list_display = ('id', 'name')
    #list_filter = []

    #search_fields = []

admin.site.register(Profile)
admin.site.register(Team, TeamAdmin)
