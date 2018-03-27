from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_order.views import web_views, create_views


urlpatterns = (
    # Summary
    path('jobs/', web_views.JobSummaryView.as_view(), name='o55_tenant_job_summary'),

    # Create
    path('jobs/create/step1/search-or-add', create_views.Step1CreateOrAddCustomerView.as_view(), name='o55_tenant_job_create'),

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
