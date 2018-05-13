from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_dashboard.views import web_views


urlpatterns = (
    url(r'^dashboard$', web_views.DashboardView.as_view(), name='workery_tenant_dashboard_master'),
)
