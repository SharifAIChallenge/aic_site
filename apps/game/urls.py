from django.conf.urls import url


from . import views

app_name = "game"
urlpatterns = [
    url(r'^scoreboard/(?P<competition_id>[0-9]+)/$', views.render_scoreboard, name='scoreboard'),
    url(r'^api/report', views.report, name='report'),
]
