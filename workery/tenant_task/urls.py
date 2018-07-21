from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_task import views


urlpatterns = (
    # Active List
    path('unassigned-tasks/', views.UnassignedTaskListView.as_view(), name='workery_tenant_unassigned_task_list'),
    path('pending-tasks/', views.PendingTaskListView.as_view(), name='workery_tenant_task_list'),
    path('closed-tasks/', views.ClosedTaskListView.as_view(), name='workery_tenant_closed_task_list'),

    # Retrieve
    path('pending-tasks/<int:pk>/', views.PendingTaskRetrieveView.as_view(), name='workery_tenant_pending_task_retrieve'),

    # Assign
    path('pending-tasks/<int:pk>/activity-sheet/', views.PendingTaskRetrieveForActivitySheetView.as_view(), name='workery_tenant_pending_task_retrieve_for_activity_sheet_retrieve'),
    path('pending-tasks/<int:pk>/activity-sheet/create', views.PendingTaskRetrieveForActivitySheetAndAssignAssociateCreateView.as_view(), name='workery_tenant_pending_task_retrieve_for_activity_sheet_retrieve_and_create'),
    path('pending-tasks/<int:pk>/activity-sheet/pending-follow-up', views.PendingTaskRetrieveForActivityFollowUpWithAssociateSheetView.as_view(), name='workery_tenant_pending_task_retrieve_for_activity_sheet_follow_up_with_associate_retrieve'),

    # Complete
    path('pending-tasks/<int:pk>/complete/', views.PendingTaskRetrieveAndCompleteCreateView.as_view(), name='workery_tenant_pending_task_retrieve_and_complete_create'),

    # Search
    path('tasks/<str:template>/search/', views.TaskSearchView.as_view(), name='workery_tenant_task_search'),
    path('tasks/<str:template>/search/results/', views.TaskSearchResultView.as_view(), name='workery_tenant_task_search_results'),
)
