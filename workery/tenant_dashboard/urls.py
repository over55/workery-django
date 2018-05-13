from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_dashboard.views import web_views


urlpatterns = (
    url(r'^dashboard$', web_views.DashboardView.as_view(), name='o55_tenant_dashboard_master'),
)
