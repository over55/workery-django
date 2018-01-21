from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_order.views import web_views


urlpatterns = (
    url(r'^orders$', web_views.master_page, name='o55_tenant_order_master'),
    url(r'^order/(?P<pk>[^/.]+)/$', web_views.detail_page, name='o55_tenant_order_detail'),
)
