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

    # Update
    path('financials/<str:template>/detail/<int:pk>/edit', views.JobUpdateView.as_view(), name='workery_tenant_financlial_job_update'),

)
