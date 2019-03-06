from django.db import models
from django.utils.crypto import get_random_string

from apps.accounts.models import Team
from suds.client import Client

from apps.game.models import TeamParticipatesChallenge

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class Transaction(models.Model):
    STATE = (
        ('u', 'unknown'),
        ('v', 'valid'),
        ('c', 'cancelled'),
    )

    team = models.ForeignKey(TeamParticipatesChallenge, related_name='transactions', null=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(choices=STATE, max_length=1)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    reference_id = models.CharField(max_length=100)
    id2 = models.CharField(max_length=100, db_index=True, blank=True, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    error = models.CharField(max_length=100, null=True, blank=True)

    @classmethod
    def begin_transaction(cls, profile, amount, callback_url, participation):
        """
        :param callback_url:
        :param participation:
        :param profile:
        :param amount: in rials
        :return: (url, transaction)
        """
        random_string = get_random_string(length=100)
        t = Transaction.objects.create(
            team=participation,
            amount=amount,
            status='u',
            id2=random_string,
        )
        username = settings.BANK_USERNAME
        password = settings.BANK_PASSWORD
        group_id = settings.BANK_GROUP_ID

        table = {1776: 48,  # 0
                 1777: 49,  # 1
                 1778: 50,  # 2
                 1779: 51,  # 3
                 1780: 52,  # 4
                 1781: 53,  # 5
                 1782: 54,  # 6
                 1783: 55,  # 7
                 1784: 56,  # 8
                 1785: 57}  # 9

        phone = profile.tel_number.translate(table)
        if len(phone) < 7:
            phone = '%s%s' % ('0' * (7 - len(phone)), phone)
        elif len(phone) > 7:
            phone = phone[-7:]

        mobile = profile.phone_number.translate(table)
        if mobile[:2] != '09':
            mobile = '09{}'.format(mobile)

        params = {
            'groupid': group_id,
            'username': username,
            'password': password,
            'bankid': 1,
            'id2': random_string,
            'callbackurl': callback_url,
            'nc': profile.national_code.translate(table),
            'name': profile.user.first_name,
            'family': profile.user.last_name,
            'tel': phone,
            'mobile': mobile,
            'email': profile.user.email,
            'amount': amount,
            'Memo': t.pk,
        }

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
        username = settings.BANK_USERNAME
        password = settings.BANK_PASSWORD
        group_id = settings.BANK_GROUP_ID


        params = {
            'groupid': group_id,
            'username': username,
            'password': password,
            'bankid': 1,
            'orderid': self.order_id
        }

        def call_webservice(params):
            cl = Client('https://payment.sharif.ir/research/ws.asmx?WSDL')
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
