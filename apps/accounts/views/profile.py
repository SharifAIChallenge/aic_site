from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from apps.accounts.forms.forms import UpdateProfileForm
from apps.accounts.models import Profile


class UpdateProfileView(LoginRequiredMixin, generic.UpdateView):
    form_class = UpdateProfileForm
    success_url = '/accounts/panel'
    template_name = 'accounts/profile/update_profile.html'
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user__pk=self.request.user.id)