from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_ongoing_order import views

urlpatterns = (
    # List
    path('ongoing-jobs/list-summary/', views.OngoingJobListView.as_view(), name='workery_tenant_ongoing_job_list'),
    # path('ongoing-jobs/list-all/', views.AllOngoingJobListView.as_view(), name='workery_tenant_all_ongoing_job_list'),

    path('ongoing-jobs/<str:template>/detail/<int:pk>/lite/', views.OngoingJobLiteRetrieveView.as_view(), name='workery_tenant_ongoing_job_lite_retrieve'),
    path('ongoing-jobs/<str:template>/detail/<int:pk>/full/', views.OngoingJobFullRetrieveView.as_view(), name='workery_tenant_ongoing_job_full_retrieve'),

)
