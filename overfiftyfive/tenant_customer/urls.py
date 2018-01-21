from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_customer.views import web_views


urlpatterns = (
    url(r'^customers$', web_views.master_page, name='o55_tenant_customer_master'),
    url(r'^customer/(?P<pk>[^/.]+)/$', web_views.detail_page, name='o55_tenant_customer_detail'),
)
