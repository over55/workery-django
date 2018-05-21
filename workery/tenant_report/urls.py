from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_report.views import ReportListView


urlpatterns = (
    url(r'^reports$', ReportListView.as_view(), name='workery_tenant_reports_list_master'),
)
