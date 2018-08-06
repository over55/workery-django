from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_ongoing_order_operation import views


urlpatterns = (
    path('ongoing-jobs/detail/<int:pk>/operation/unassign', views.OngoingWorkOrderUnassignOperationView.as_view(), name='workery_tenant_ongoing_job_unassign_operation'),
    path('ongoing-jobs/detail/<int:pk>/operation/close', views.OngoingWorkOrderCloseOperationView.as_view(), name='workery_tenant_ongoing_job_close_operation')
)
