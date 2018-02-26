from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.game.models import TeamParticipatesChallenge


def payment_required(view):
    def wrap(request, *args, **kwargs):
        if kwargs['participation_id']:
            participation_id = kwargs['participation_id']
            participation = TeamParticipatesChallenge.objects.get(id=participation_id)
        else:
            participation = request.user.profile.panel_active_teampc

        if (not participation.should_pay) or participation.has_paid:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('billing:request_payment', args=[participation_id]))

    wrap.__doc__ = view.__doc__
    wrap.__name__ = view.__name__
    return wrap
