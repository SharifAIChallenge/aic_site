"""aic_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from apps.intro import urls as intro_urls
from apps.accounts import urls as account_urls
from apps.game import urls as game_urls
from zinnia import urls as zinnia_urls
from apps.game import urls as game_urls
from apps.billing import urls as billing_urls
from apps.modir import urls as modir_urls
from apps.modir.views import redirect_shortened_url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(intro_urls)),

    url(r'^accounts/password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^accounts/password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^accounts/reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    #
    url(r'^accounts/', include(account_urls)),
    # url(r'^blog/', include(zinnia_urls)),
    url(r'^game/', include(game_urls)),
    # url(r'^articles/comments/', include('django_comments.urls')),
    # url(r'^tinymce/filebrowser/', include('zinnia_tinymce.urls')),
    # url(r'^tinymce/', include('tinymce.urls')),
    # url(r'^billing/', include(billing_urls)),
    url(r'^go/', include(modir_urls))
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)