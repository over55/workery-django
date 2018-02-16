from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_customer.views import web_views


urlpatterns = (
    path('customers/', web_views.CustomerListView.as_view(), name='o55_tenant_customer_list'),
    path('customer/create', web_views.CustomerCreateView.as_view(), name='o55_tenant_customer_create'),
    path('customer/<int:pk>/', web_views.CustomerDetailView.as_view(), name='o55_tenant_customer_detail'),

    # url(r'^customer/create$', web_views.create_page, name='o55_tenant_customer_create'),
    # url(r'^customer/(?P<pk>[^/.]+)/$', web_views.retrieve_or_update_page, name='o55_tenant_customer_retrieve_or_update'),
)
