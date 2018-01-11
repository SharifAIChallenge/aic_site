from django.contrib import admin

# Register your models here.
from apps.accounts.models import Profile

admin.site.register(Profile)