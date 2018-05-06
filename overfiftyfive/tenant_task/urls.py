from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_task import views


urlpatterns = (
    # Active List
    path('pending-tasks/', views.PendingTaskListView.as_view(), name='o55_tenant_task_list'),
    path('closed-tasks/', views.ClosedTaskListView.as_view(), name='o55_tenant_closed_task_list'),

    # Update / Retrieve
    path('pending-tasks/<int:pk>/', views.PendingTaskRetrieveView.as_view(), name='o55_tenant_pending_task_retrieve'),
    path('pending-tasks/<int:pk>/activity-sheet/', views.PendingTaskRetrieveActivitySheetView.as_view(), name='o55_tenant_pending_task_activity_sheet_retrieve'),
    path('pending-tasks/<int:pk>/activity-sheet/create', views.PendingTaskRetrieveActivitySheetAndAssignAssociateView.as_view(), name='o55_tenant_pending_task_activity_sheet_retrieve_and_create'),
)
