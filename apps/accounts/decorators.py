from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


def complete_profile_required(view):
    def wrap(request, *args, **kwargs):
        if request.user.profile.is_complete:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('accounts:update_profile'))

    wrap.__doc__ = view.__doc__
    wrap.__name__ = view.__name__
    return wrapN


def complete_team_required(view):
    def wrap(request, *args, **kwargs):
        if request.user.profile.panel_active_teampc.is_complete:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(
                reverse(
                    'accounts:add_participation',
                    args=[request.user.profile.panel_active_teampc.id]
                )
            )

    wrap.__doc__ = view.__doc__
    wrap.__name__ = view.__name__
    return wrap
