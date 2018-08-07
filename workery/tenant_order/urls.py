from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_order.views import create_views, list_view, retrieve_view, search_view, update_views


urlpatterns = (
    # Summary
    path('jobs/summary/', list_view.JobSummaryView.as_view(), name='workery_tenant_job_summary'),

    # Create
    path('jobs/create/step-1/search-or-add', create_views.Step1ACreateOrAddCustomerView.as_view(), name='workery_tenant_job_search_or_add_create'),
    path('jobs/create/step-1/search-results', create_views.Step1BCustomerSearchResultsView.as_view(), name='workery_tenant_job_customer_search_results_create'),
    path('jobs/create/step-2/', create_views.Step2View.as_view(), name='workery_tenant_job_step_2_create'),
    path('jobs/create/step-3/', create_views.Step3View.as_view(), name='workery_tenant_job_step_3_create'),
    path('jobs/create/step-4/', create_views.Step4View.as_view(), name='workery_tenant_job_step_4_create'),
    path('jobs/create/step-5/', create_views.Step5View.as_view(), name='workery_tenant_job_step_5_create'),

    # List
    path('jobs/list/', list_view.JobListView.as_view(), name='workery_tenant_job_list'),
    path('archived-jobs/list/', list_view.ArchivedJobListView.as_view(), name='workery_tenant_job_archive_list'),
    path('jobs/comments/', list_view.JobCommentsListView.as_view(), name='workery_tenant_job_comments_list'),

    # Search
    path('jobs/search/', search_view.JobSearchView.as_view(), name='workery_tenant_job_search'),
    path('jobs/search/results/', search_view.JobSearchResultView.as_view(), name='workery_tenant_job_search_results'),

    # Retrieve
    path('jobs/<str:template>/detail/<int:pk>/lite/', retrieve_view.JobLiteRetrieveView.as_view(), name='workery_tenant_job_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/full/', retrieve_view.JobFullRetrieveView.as_view(), name='workery_tenant_job_full_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/activity-sheet/', retrieve_view.JobRetrieveForActivitySheetListView.as_view(), name='workery_tenant_job_retrieve_for_activity_sheet_list'),
    path('jobs/<str:template>/detail/<int:pk>/tasks/', retrieve_view.JobRetrieveForTasksListView.as_view(), name='workery_tenant_job_retrieve_for_tasks_list'),
    path('jobs/<str:template>/detail/<int:pk>/comments/', retrieve_view.JobRetrieveForCommentsListAndCreateView.as_view(), name='workery_tenant_job_comments_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/close/', retrieve_view.JobRetrieveForCloseCreateView.as_view(), name='workery_tenant_job_retrieve_for_close_create'),
    path('jobs/<str:template>/detail/<int:pk>/postpone/', retrieve_view.JobRetrieveForPostponeCreateView.as_view(), name='workery_tenant_job_retrieve_for_postpone_create'),
    path('jobs/<str:template>/detail/<int:pk>/reopen/', retrieve_view.JobRetrieveForReopeningCreateView.as_view(), name='workery_tenant_job_retrieve_for_reopen_create'),
    path('archived-jobs/detail/<int:pk>/full/', retrieve_view.ArchivedJobFullRetrieveView.as_view(), name='workery_tenant_job_archive_full_retrieve'),

    # Update
    path('jobs/<str:template>/detail/<int:pk>/edit/', update_views.JobUpdateView.as_view(), name='workery_tenant_job_update'),
)
