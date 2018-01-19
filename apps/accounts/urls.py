from django.conf.urls import url

from apps.accounts import views

urlpatterns = [
    url(r'signup/$', views.SignupView.as_view(), name='signup'),
    url(r'login/$', views.LoginView.as_view(), name='login'),
    url(r'logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'update_profile/$', views.UpdateProfileView.as_view(), name='update profile'),
    url(r'panel/(?P<participation_id>[0-9]+)?$', views.panel, name='panel'),
]
