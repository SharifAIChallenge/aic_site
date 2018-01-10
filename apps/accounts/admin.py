from django.contrib import admin

# Register your models here.
from apps.accounts.models import Team, UserParticipatesOnTeam

admin.site.register(Team)
admin.site.register(UserParticipatesOnTeam)
