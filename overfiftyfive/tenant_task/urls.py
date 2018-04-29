from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_task import views


urlpatterns = (
    # Summary
    path('tasks/', views.ActiveTaskListView.as_view(), name='o55_tenant_task_list'),

    # # Retrieve
    # path('task/<int:pk>/', views.ResourceCategoryRetrieveView.as_view(), name='o55_tenant_resource_category_retrieve'),
)
