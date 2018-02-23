from django.conf.urls import url
from apps.billing import views

app_name = "billing"
urlpatterns = [
    url("^pay/(?P<participation_id>[0-9]+)$", views.payment, name='request_payment'),
    url("^payments/(?P<participation_id>[0-9]+)$", views.payments_list, name='payments_list'),
    url("^complete/(?P<participation_id>[0-9]+)/$", views.complete_payment, name='complete_payment'),
]