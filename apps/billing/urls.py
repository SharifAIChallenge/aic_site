from django.conf.urls import patterns, url

urlpatterns = patterns(
    'billing.views',
    url("^pay/", 'payment', name='request_payment'),
    url("^payments/$", 'payments_list', name='payments_list'),
    url("^complete/", 'complete_payment', name='complete_payment'),
)