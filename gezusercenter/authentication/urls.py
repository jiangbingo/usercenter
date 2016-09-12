# -- encoding: utf-8 --
__author__ = 'PD-002'

from authentication.views import CheckUser, MapUser, vsersion
from django.conf.urls import url

urlpatterns = [
    url(r'^check/$', CheckUser.check, name="check"),
    url(r'^map/$', MapUser.map, name="map"),
    url(r'^$', vsersion, name="map"),
]
