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
from django.conf.urls import url, include
from django.contrib import admin
from apps.intro import urls as intro_urls
from apps.accounts import urls as account_urls
from apps.game import urls as game_urls
from zinnia import urls as zinnia_urls
from apps.game import urls as game_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(intro_urls)),
    url(r'^accounts/', include(account_urls)),
    url(r'^blog/', include(zinnia_urls)),
    url(r'^game/', include(game_urls)),
    url(r'^articles/comments/', include('django_comments.urls')),
    url(r'^captcha/', include('captcha.urls')),
]
