from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_financial import views
from tenant_order.views import create_views, list_view, retrieve_view, search_view, update_views


urlpatterns = (
    # Active List
    path('financials/unpaid-jobs/', views.UnpaidJobOrderListView.as_view(), name='workery_tenant_unpaid_jobs_list'),
    path('financials/paid-jobs/', views.PaidJobOrderListView.as_view(), name='workery_tenant_paid_jobs_list'),
    path('financials/all-jobs/', views.AllJobOrderListView.as_view(), name='workery_tenant_all_jobs_list'),

    # Retrieve
    path('financials/<str:template>/detail/<int:pk>/', views.JobRetrieveView.as_view(), name='workery_tenant_financlial_job_retrieve'),
    path('jobs/<str:template>/detail/<int:pk>/lite/', retrieve_view.JobLiteRetrieveView.as_view(), name='workery_tenant_job_retrieve'),

    # Update
    path('financials/<str:template>/detail/<int:pk>/edit', views.JobUpdateView.as_view(), name='workery_tenant_financlial_job_update'),

    # Search
    path('financials/<str:template>/search/', views.WorkOrderSearchView.as_view(), name='workery_tenant_financlial_job_search'),
    path('financials/<str:template>/search/results/', views.WorkOrderSearchResultView.as_view(), name='workery_tenant_financlial_job_search_results'),
)
