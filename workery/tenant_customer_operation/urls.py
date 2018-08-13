from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_customer_operation import views


urlpatterns = (
    path('clients/<str:template>/detail/<int:pk>/operation/upgrade-residential/', views.ResidentialCustomerUpgradeOperationView.as_view(), name='workery_tenant_residential_customer_upgrade_operation'),
)
