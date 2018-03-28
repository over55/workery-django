from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_order.views import web_views, create_views


urlpatterns = (
    # Summary
    path('jobs/', web_views.JobSummaryView.as_view(), name='o55_tenant_job_summary'),

    # Create
    path('jobs/create/step-1/search-or-add', create_views.Step1CreateOrAddCustomerView.as_view(), name='o55_tenant_job_search_or_add_create'),
    path('jobs/create/step-1/search-results', create_views.Step1CustomerSearchResultsView.as_view(), name='o55_tenant_job_customer_search_results_create'),
    path('jobs/create/step-1/add-customer', create_views.Step1AddCustomerView.as_view(), name='o55_tenant_job_add_customer_create'),
    path('jobs/create/step-1/add-customer-confirmation', create_views.Step1AddCustomerConfirmationView.as_view(), name='o55_tenant_job_add_customer_confirmation_create'),
    path('jobs/create/step-2/', create_views.Step2View.as_view(), name='o55_tenant_job_step_2_create'),
    path('jobs/create/step-3/', create_views.Step3View.as_view(), name='o55_tenant_job_step_3_create'),
    path('jobs/create/step-4/', create_views.Step4View.as_view(), name='o55_tenant_job_step_4_create'),
    path('jobs/create/step-5/', create_views.Step5View.as_view(), name='o55_tenant_job_step_5_create'),

    # List
    path('jobs/list/', web_views.JobListView.as_view(), name='o55_tenant_job_list'),

    # Search
    path('jobs/search/', web_views.JobSearchView.as_view(), name='o55_tenant_job_search'),
    path('jobs/search/results/', web_views.JobSearchResultView.as_view(), name='o55_tenant_job_search_results'),

    # Retrieve
    path('jobs/detail/<str:template>/<int:pk>/', web_views.JobRetrieveView.as_view(), name='o55_tenant_job_retrieve'),

    # Update
    path('jobs/detail/<str:template>/<int:pk>/edit/', web_views.JobUpdateView.as_view(), name='o55_tenant_job_update'),
)
