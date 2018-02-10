from django.conf.urls import url


from . import views

app_name = "game"
urlpatterns = [
    url(r'^scoreboard/(?P<competition_id>[0-9]+)/$', views.render_scoreboard, name='scoreboard'),
    url(r'^api/report', views.report, name='report'),
    url(r'^game_viewer', views.game_view(), name='game viewer'),
    url(r'^map_maker', views.map_maker(), name='map maker'),
]
