# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from shared_home import views


urlpatterns = (
    url(r'^$', views.index_page, name='o55_index_master'),
    url(r'^en$', views.index_page),
    url(r'^en/$', views.index_page),
    url(r'^404$', views.handler404, name='o55_http_404_master'),
    url(r'^500$', views.handler500, name='o55_http_500_master'),
)
