from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^scoreboard/(?P<competition_id>[0-9]+)/$', views.scoreboard, name='scoreboard'),

]



