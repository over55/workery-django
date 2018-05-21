from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_financial import views


urlpatterns = (
    # # Active List
    path('financials/unpaid-jobs/', views.UnpaidJobOrderListView.as_view(), name='workery_tenant_unpaid_jobs_list'),
    path('financials/paid-jobs/', views.PaidJobOrderListView.as_view(), name='workery_tenant_paid_jobs_list'),
    path('financials/all-jobs/', views.AllJobOrderListView.as_view(), name='workery_tenant_all_jobs_list'),

    # Retrieve
    path('financials/<str:template>/detail/<int:pk>/', views.JobRetrieveView.as_view(), name='workery_tenant_financlial_job_retrieve'),

    # # Assign
    # path('pending-tasks/<int:pk>/activity-sheet/', views.PendingTaskRetrieveForActivitySheetView.as_view(), name='workery_tenant_pending_task_retrieve_for_activity_sheet_retrieve'),
    # path('pending-tasks/<int:pk>/activity-sheet/create', views.PendingTaskRetrieveForActivitySheetAndAssignAssociateCreateView.as_view(), name='workery_tenant_pending_task_retrieve_for_activity_sheet_retrieve_and_create'),
    #
    # # Complete
    # path('pending-tasks/<int:pk>/complete/', views.PendingTaskRetrieveAndCompleteCreateView.as_view(), name='workery_tenant_pending_task_retrieve_and_complete_create'),

)
