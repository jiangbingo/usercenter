# -- encoding: utf-8 --
__author__ = 'PD-002'

from django.conf.urls import url

from .views import Location

urlpatterns = [
    # 用户注册
    url(r'^location/$', Location.get, name="location"),
]
