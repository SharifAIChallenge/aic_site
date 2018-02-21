from django.db import models
from django.utils.crypto import get_random_string

from apps.accounts.models import Team
from suds.client import Client

from apps.game.models import TeamParticipatesChallenge

from aic_site.settings import production_secret


class Transaction(models.Model):
    STATE = (
        ('u', 'unknown'),
        ('v', 'valid'),
        ('c', 'cancelled'),
    )
    BANK = {
        'mellat': 1, 'tejarat': 2
    }

    team = models.ForeignKey(TeamParticipatesChallenge, related_name='transactions', null=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(choices=STATE, max_length=1)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    bank = models.CharField(max_length=20, choices=[(str(v), k) for k, v in BANK.items()])
    reference_id = models.CharField(max_length=100)
    id2 = models.CharField(max_length=100, db_index=True, blank=True, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    error = models.CharField(max_length=100, null=True, blank=True)

    @classmethod
    def begin_transaction(cls, profile, amount, callback_url, participation, bank='mellat'):
        """
        :param profile:
        :param amount: in rials
        :param bank: 'mellat' or 'tejarat'
        :return: (url, transaction)
        """
        random_string = get_random_string(length=100)
        t = Transaction.objects.create(
            team=participation,
            amount=amount,
            status='u',
            bank=bank,
            id2=random_string,
        )
        username = production_secret.BANK_USERNAME
        password = production_secret.BANK_PASSWORD
        group_id = production_secret.BANK_GROUP_ID

        phone = profile.tel_number
        if len(phone) < 7:
            phone = '%s%s' % ('0' * (7 - len(phone)), phone)
        elif len(phone) > 7:
            phone = phone[-7:]

        mobile = profile.phone_number
        if mobile[:2] != '09':
            mobile = '09{}'.format(mobile)

        params = {
            'groupid': group_id,
            'username': username,
            'password': password,
            'bankid': cls.BANK[bank],
            'id2': random_string,
            'callbackurl': callback_url,
            'nc': profile.national_code,
            'name': profile.user.first_name,
            'family': profile.user.last_name,
            'tel': phone,
            'mobile': mobile,
            'email': profile.user.email,
            'amount': amount,
            'Memo': t.pk,
        }
        print('callbackurl: ')
        print(params['callbackurl'])

        def call_webservice(params):
            cl = Client('https://payment.sharif.ir/research/ws.asmx?WSDL')
            return cl.service.Request(**params)

        rescode, order_id = call_webservice(params).split(',')

        if rescode == '0':
            t.order_id = order_id
            t.save()
            return 'http://payment.sharif.ir/research/submit.aspx?orderid={}'.format(order_id), t
        else:
            t.status = 'c'
            t.error = order_id
            t.save()
            return '', t

    def update_status(self):
        username = production_secret.BANK_USERNAME
        password = production_secret.BANK_PASSWORD
        group_id = production_secret.BANK_GROUP_ID

        params = {
            'groupid': group_id,
            'username': username,
            'password': password,
            'bankid': self.BANK[self.bank],
            'orderid': self.order_id
        }

        def call_webservice(params):
            cl = Client('https://payment.sharif.ir/research/ws.asmx')
            return cl.service.Status(**params)

        vercode, reference_id = call_webservice(params).split(':')
        if vercode == '0':
            self.status = 'v'
            self.reference_id = reference_id
        else:
            self.status = 'c'
            self.error = reference_id
        self.save()

        return reference_id
