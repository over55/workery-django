from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_task import views


urlpatterns = (
    # Active List
    path('pending-tasks/', views.ActiveTaskListView.as_view(), name='o55_tenant_task_list'),
    path('closed-tasks/', views.ClosedTaskListView.as_view(), name='o55_tenant_closed_task_list'),

    # Update / Retrieve
    path('task/<int:pk>/', views.TaskRetrieveUpdateView.as_view(), name='o55_tenant_task_retrieve_update'),
)
