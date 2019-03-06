from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from apps.accounts.decorators import complete_team_required
from apps.billing.forms.forms import UserCompletionForm
from apps.game.models import TeamParticipatesChallenge
from .models import Transaction

import logging

logger = logging.getLogger(__name__)


@login_required
@complete_team_required
def payment(request, participation_id):
    participation = get_object_or_404(TeamParticipatesChallenge, id=participation_id)
    if not participation.should_pay or participation.has_paid:
        return HttpResponseRedirect(reverse('accounts:panel'))
    if request.method == 'POST':
        callback_url = request.build_absolute_uri(
            reverse(
                'billing:complete_payment',
                args=[participation_id]
            )) + '?'

        logger.error(callback_url)

        profile = request.user.profile

        url, t = Transaction.begin_transaction(profile=profile,
                                               amount=participation.challenge.entrance_price,
                                               callback_url=callback_url,
                                               participation=participation,
                                               )
        if url:
            return HttpResponseRedirect(url)
        else:
            return render(request, 'billing/bank_payment_error.html', context={
                'error': t.error,
                'participation': participation,
                'participation_id': participation_id,
            })
    else:
        error = None
        unverified_transaction = participation.transactions.filter(status='u')
        if unverified_transaction.exists():
            unverified_transaction.all()[0].update_status()

        if participation.transactions.filter(status='u').exists():
            error = _("You have unverified payment(s).")
        if not participation.should_pay:
            error = _("There is nothing to pay for.")
        if participation.transactions.filter(status='v').exists():
            error = _("You have already paid.")

        if error:
            return render(request, 'billing/bank_payment_error.html', context={
                'error': error,
                'participation': participation,
                'participation_id': participation_id,
            })

        return render(request, 'billing/bank_payment.html', {
            'participation': participation
        })


@login_required
# @team_required_and_finalized
def complete_payment(request, participation_id):
    participation = get_object_or_404(TeamParticipatesChallenge, id=participation_id)
    our_id = request.GET.get('id2', None)
    if not our_id:
        raise PermissionDenied()

    transaction = get_object_or_404(Transaction, id2=our_id)
    transaction.update_status()

    if transaction.status == 'v':
        return render(request, 'billing/bank_payment_success.html')
    elif transaction.status == 'c':
        return render(request, 'billing/bank_payment_error.html', context={
            'error': transaction.error,
            'participation': participation,
            'participation_id': participation_id
        })
    else:
        return redirect('billing:payments_list')


@login_required
# @team_required_and_finalized
def payments_list(request, participation_id):
    participation = get_object_or_404(TeamParticipatesChallenge, id=participation_id)
    unknown_payments = Transaction.objects.filter(status='u')
    for transaction in unknown_payments:
        transaction.update_status()
    payments = participation.transactions.all()
    return render(request, 'billing/bank_payments_list.html', {
        'payments': payments,
        'participation': participation
    })
