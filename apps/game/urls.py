from django.conf.urls import url
from apps.game import views

app_name = "game"
urlpatterns = [
    url(r'^scoreboard/$', views.score_board_test, name='scoreboard'),
]
