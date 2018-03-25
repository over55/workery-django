from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_customer.views import web_views


urlpatterns = (
    # Summary
    path('clients/', web_views.CustomerSummaryView.as_view(), name='o55_tenant_customer_summary'),

    # Create
    path('clients/create/', web_views.CustomerCreateView.as_view(), name='o55_tenant_customer_create'),

    # List
    path('clients/list/', web_views.CustomerListView.as_view(), name='o55_tenant_customer_list'),

    # Search
    path('clients/search/', web_views.CustomerSearchView.as_view(), name='o55_tenant_customer_search'),
    path('clients/search/results/', web_views.CustomerSearchResultView.as_view(), name='o55_tenant_customer_search_results'),

    # Retrieve
    path('clients/detail/<str:template>/<int:pk>/', web_views.CustomerRetrieveView.as_view(), name='o55_tenant_customer_retrieve'),

    # Update
    path('clients/detail/<str:template>/<int:pk>/edit/', web_views.CustomerUpdateView.as_view(), name='o55_tenant_customer_update'),
)
