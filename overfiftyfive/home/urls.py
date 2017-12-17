from django.conf.urls import include, url
from home import views


urlpatterns = (
    url(r'^$', views.index_page, name='o55_index_master'),
    url(r'^en$', views.index_page),
    url(r'^en/$', views.index_page),
)
