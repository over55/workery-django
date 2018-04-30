from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_order.views import create_views, list_view, retrieve_view, search_view, update_views


urlpatterns = (
    # Summary
    path('jobs/summary/', list_view.JobSummaryView.as_view(), name='o55_tenant_job_summary'),

    # Create
    path('jobs/create/step-1/search-or-add', create_views.Step1A1CreateOrAddCustomerView.as_view(), name='o55_tenant_job_search_or_add_create'),
    path('jobs/create/step-1/search-results', create_views.Step1A2CustomerSearchResultsView.as_view(), name='o55_tenant_job_customer_search_results_create'),
    path('jobs/create/step-1/pick-customer-type', create_views.Step1B1PickCustomerView.as_view(), name='o55_tenant_job_pick_add_customer_type'),
    path('jobs/create/step-1/add-residential-customer', create_views.Step1B2AAddResidentialCustomerView.as_view(), name='o55_tenant_job_add_residential_customer_create'),
    path('jobs/create/step-1/add-residential-customer-confirmation', create_views.Step1B2BAddCustomerConfirmationView.as_view(), name='o55_tenant_job_add_residential_customer_confirmation'),
    path('jobs/create/step-1/add-commercial-customer', create_views.Step1B3AAddCommercialCustomerView.as_view(), name='o55_tenant_job_add_commercial_customer_create'),
    path('jobs/create/step-1/add-commercial-customer-confirmation', create_views.Step1B3BAddCommercialConfirmationView.as_view(), name='o55_tenant_job_add_commercial_customer_confirmation'),
    path('jobs/create/step-2/', create_views.Step2View.as_view(), name='o55_tenant_job_step_2_create'),
    path('jobs/create/step-3/', create_views.Step3View.as_view(), name='o55_tenant_job_step_3_create'),
    path('jobs/create/step-4/', create_views.Step4View.as_view(), name='o55_tenant_job_step_4_create'),
    path('jobs/create/step-5/', create_views.Step5View.as_view(), name='o55_tenant_job_step_5_create'),
    path('jobs/create/step-6/', create_views.Step6View.as_view(), name='o55_tenant_job_step_6_create'),

    # List
    path('jobs/list/', list_view.JobListView.as_view(), name='o55_tenant_job_list'),

    # Search
    path('jobs/search/', search_view.JobSearchView.as_view(), name='o55_tenant_job_search'),
    path('jobs/search/results/', search_view.JobSearchResultView.as_view(), name='o55_tenant_job_search_results'),

    # Retrieve
    path('jobs/<str:template>/detail/<int:pk>/', retrieve_view.JobRetrieveView.as_view(), name='o55_tenant_job_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/comments/', retrieve_view.JobCommentsRetrieveView.as_view(), name='o55_tenant_job_comments_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/activity-sheet/', retrieve_view.JobActivitySheetRetrieveView.as_view(), name='o55_tenant_job_activity_sheet_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/activity-sheet/create', retrieve_view.JobActivitySheetCreateAndRetrieveView.as_view(), name='o55_tenant_job_activity_sheet_retrieve_and_create'),

    # Update
    path('jobs/<str:template>/detail/<int:pk>/edit/', update_views.JobUpdateView.as_view(), name='o55_tenant_job_update'),
)
