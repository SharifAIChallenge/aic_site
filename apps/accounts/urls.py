from django.conf.urls import url

from apps.accounts import views

urlpatterns = [
    url(r'signup/$', views.SignupView.as_view(), name='signup')
]
