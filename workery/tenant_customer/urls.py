from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_customer.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('clients/summary/', list_view.CustomerSummaryView.as_view(), name='workery_tenant_customer_summary'),

    # Create
    path('clients/create/pick', create_view.PickCustomerTypeInCreateView.as_view(), name='workery_tenant_pick_customer_create'),
    path('clients/create/residential', create_view.ResidentialCustomerCreateView.as_view(), name='workery_tenant_residential_customer_create'),
    path('clients/create/residential/confirm', create_view.ResidentialCustomerConfirmCreateView.as_view(), name='workery_tenant_residential_customer_confirm_create'),
    path('clients/create/commercial', create_view.CommercialCustomerCreateView.as_view(), name='workery_tenant_commercial_customer_create'),
    path('clients/create/commercial/confirm', create_view.CommercialCustomerConfirmCreateView.as_view(), name='workery_tenant_commercial_customer_confirm_create'),

    # List
    path('clients/list/', list_view.CustomerListView.as_view(), name='workery_tenant_customer_list'),

    # Search
    path('clients/search/', search_view.CustomerSearchView.as_view(), name='workery_tenant_customer_search'),
    path('clients/search/results/', search_view.CustomerSearchResultView.as_view(), name='workery_tenant_customer_search_results'),

    # Retrieve
    path('clients/<str:template>/detail/<int:pk>/lite/', retrieve_view.CustomerLiteRetrieveView.as_view(), name='workery_tenant_customer_lite_retrieve'),
    path('clients/<str:template>/detail/<int:pk>/full/', retrieve_view.CustomerFullRetrieveView.as_view(), name='workery_tenant_customer_full_retrieve'),
    path('clients/<str:template>/detail/<int:pk>/jobs/', retrieve_view.CustomerRetrieveForJobsListView.as_view(), name='workery_tenant_customer_retrieve_for_jobs_list'),
    path('clients/<str:template>/detail/<int:pk>/files/', retrieve_view.CustomerRetrieveForFilesListView.as_view(), name='workery_tenant_customer_retrieve_for_files_list'),
    path('clients/<str:template>/detail/<int:pk>/comments/', retrieve_view.CustomerRetrieveForCommentListAndCreateView.as_view(), name='workery_tenant_customer_retrieve_for_comment_list_and_create'),

    # Update
    path('clients/<str:template>/residential-detail/<int:pk>/edit/', update_view.ResidentialCustomerUpdateView.as_view(), name='workery_tenant_residential_customer_update'),
    path('clients/<str:template>/residential-detail/<int:pk>/deactivation/', update_view.DeactivateCustomerUpdateView.as_view(), name='workery_tenant_residential_deactivate_customer_update'),
    path('clients/<str:template>/commercial-detail/<int:pk>/edit/', update_view.CommercialCustomerUpdateView.as_view(), name='workery_tenant_commercial_customer_update'),
    path('clients/<str:template>/commercial-detail/<int:pk>/deactivation/', update_view.DeactivateCustomerUpdateView.as_view(), name='workery_tenant_commercial_deactivate_customer_update'),
)
