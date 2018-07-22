from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_order_operation import views


urlpatterns = (
    #
    # Completed Work Orders
    #
    path('jobs/detail/<int:pk>/operation/closed-job/unassign', views.CompletedWorkOrderUnassignOperationView.as_view(), name='workery_tenant_completed_job_unassign_operation'),
    path('jobs/detail/<int:pk>/operation/closed-job/close', views.CompletedWorkOrderCloseOperationView.as_view(), name='workery_tenant_completed_job_close_operation'),

    #
    # Non-Completed Work Orders
    #

    # path('jobs/<str:template>/detail/<int:pk>/operation/open-job/closed',
    # # path('jobs/operation/<int:pk>/unassign-for-completed',
    # views.CompletedWorkOrderUnassignOperationView.as_view(),
    # name='workery_tenant_completed_job_unassign_operation'),

    # path('jobs/<str:template>/detail/<int:pk>/operation/open-job/postpone',
    # # path('jobs/operation/<int:pk>/unassign-for-completed',
    # views.CompletedWorkOrderUnassignOperationView.as_view(),
    # name='workery_tenant_completed_job_unassign_operation'),

    # path('jobs/<str:template>/detail/<int:pk>/operation/open-job/unassign',
    # # path('jobs/operation/<int:pk>/unassign-for-completed',
    # views.CompletedWorkOrderUnassignOperationView.as_view(),
    # name='workery_tenant_completed_job_unassign_operation'),

    # path('jobs/<str:template>/detail/<int:pk>/operation/open-job/re-open',
    # # path('jobs/operation/<int:pk>/unassign-for-completed',
    # views.CompletedWorkOrderUnassignOperationView.as_view(),
    # name='workery_tenant_completed_job_unassign_operation'),
)
