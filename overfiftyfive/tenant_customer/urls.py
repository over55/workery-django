from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_customer.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('clients/summary/', list_view.CustomerSummaryView.as_view(), name='o55_tenant_customer_summary'),

    # Create
    path('clients/create/pick', create_view.PickCustomerTypeInCreateView.as_view(), name='o55_tenant_pick_customer_create'),
    path('clients/create/residential', create_view.ResidentialCustomerCreateView.as_view(), name='o55_tenant_residential_customer_create'),
    path('clients/create/residential/confirm', create_view.ResidentialCustomerConfirmCreateView.as_view(), name='o55_tenant_residential_customer_confirm_create'),
    path('clients/create/commercial', create_view.CommercialCustomerCreateView.as_view(), name='o55_tenant_commercial_customer_create'),
    path('clients/create/commercial/confirm', create_view.CommercialCustomerConfirmCreateView.as_view(), name='o55_tenant_commercial_customer_confirm_create'),

    # List
    path('clients/list/', list_view.CustomerListView.as_view(), name='o55_tenant_customer_list'),

    # Search
    path('clients/search/', search_view.CustomerSearchView.as_view(), name='o55_tenant_customer_search'),
    path('clients/search/results/', search_view.CustomerSearchResultView.as_view(), name='o55_tenant_customer_search_results'),

    # Retrieve
    path('clients/<str:template>/detail/<int:pk>/', retrieve_view.CustomerRetrieveView.as_view(), name='o55_tenant_customer_retrieve'),
    path('clients/<str:template>/details/comments/<int:pk>/', retrieve_view.CustomerCommentRetrieveView.as_view(), name='o55_tenant_customer_comments_retrieve'),

    # Update
    path('clients/<str:template>/detail/<int:pk>/edit/', update_view.CustomerUpdateView.as_view(), name='o55_tenant_customer_update'),
)
