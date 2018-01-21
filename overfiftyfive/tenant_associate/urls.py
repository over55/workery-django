from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_associate.views import web_views


urlpatterns = (
    url(r'^associates$', web_views.master_page, name='o55_tenant_associate_master'),
    url(r'^associates/(?P<pk>[^/.]+)/$', web_views.detail_page, name='o55_tenant_associate_detail'),
)
