from django.conf.urls import url
from apps.accounts import views

app_name = "accounts"
urlpatterns = [
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^update_profile/$', views.UpdateProfileView.as_view(), name='update_profile'),
    url(r'^create_team/(?P<challenge_id>[0-9]+)$', views.create_team, name='create_team'),
    url(r'^create_team/success_create_team$', views.success_create_team, name='success_create_team'),
    url(r'^panel/(?P<participation_id>[0-9]+)?$', views.panel, name='panel'),
    url(r'^panel/accept_participation/(?P<participation_id>[0-9]+)$', views.accept_participation,
        name='accept_participation'),
    url(r'^panel/reject_participation/(?P<participation_id>[0-9]+)$', views.reject_participation,
        name='reject_participation'),
    url(r'^panel/set_final_submission/(?P<submission_id>[0-9]+)', views.set_final_submission,
        name='set final submission'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
