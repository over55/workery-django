from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_order_operation import views


urlpatterns = (

    #
    # Completed Work Orders
    #

    path(
        'jobs/detail/<int:pk>/operation/closed-job/unassign',
        views.CompletedWorkOrderUnassignOperationView.as_view(),
        name='workery_tenant_completed_job_unassign_operation'
    ),
    path(
        'jobs/detail/<int:pk>/operation/closed-job/close',
        views.CompletedWorkOrderCloseOperationView.as_view(),
        name='workery_tenant_completed_job_close_operation'
    ),
    path(
        'jobs/detail/<int:pk>/operation/closed-job/cancel',
        views.CompletedWorkOrderCancelOperationView.as_view(),
        name='workery_tenant_completed_job_cancel_operation'
    ),

    #
    # Non-Completed Work Orders
    #

    path(
        'jobs/detail/<int:pk>/operation/unassign/',
        views.IncompletedWorkOrderUnassignOperationView.as_view(),
        name='workery_tenant_job_retrieve_for_unassign_create'
    )

)
