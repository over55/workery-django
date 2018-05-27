from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_report.views.web_views import (
    ReportListView,
    Report01DetailView,
    Report05DetailView,
    Report06DetailView,
    Report07DetailView,
    Report08DetailView,
    Report09DetailView,
    Report10DetailView,
    Report12DetailView
)
from tenant_report.views.csv_views import (
    report_01_streaming_csv_view,
    report_05_streaming_csv_view,
    report_06_streaming_csv_view,
    report_07_streaming_csv_view,
    report_08_streaming_csv_view,
    report_09_streaming_csv_view,
    report_10_streaming_csv_view,
    report_12_streaming_csv_view
)

urlpatterns = (
    url(r'^reports$', ReportListView.as_view(), name='workery_tenant_reports_list_master'),
    url(r'^report/1/$', Report01DetailView.as_view(), name='workery_tenant_report_01_detail_master'),
    url(r'^report/5/$', Report05DetailView.as_view(), name='workery_tenant_report_05_detail_master'),
    url(r'^report/6/$', Report06DetailView.as_view(), name='workery_tenant_report_06_detail_master'),
    url(r'^report/7/$', Report07DetailView.as_view(), name='workery_tenant_report_07_detail_master'),
    url(r'^report/8/$', Report08DetailView.as_view(), name='workery_tenant_report_08_detail_master'),
    url(r'^report/9/$', Report09DetailView.as_view(), name='workery_tenant_report_09_detail_master'),
    url(r'^report/10/$', Report10DetailView.as_view(), name='workery_tenant_report_10_detail_master'),
    url(r'^report/12/$', Report12DetailView.as_view(), name='workery_tenant_report_12_detail_master'),

    url(r'^report/1/csv-download$', report_01_streaming_csv_view, name='workery_tenant_report_01_download_csv_file_api_endpoint'),
    url(r'^report/5/csv-download$', report_05_streaming_csv_view, name='workery_tenant_report_05_download_csv_file_api_endpoint'),
    url(r'^report/6/csv-download$', report_06_streaming_csv_view, name='workery_tenant_report_06_download_csv_file_api_endpoint'),
    url(r'^report/7/csv-download$', report_07_streaming_csv_view, name='workery_tenant_report_07_download_csv_file_api_endpoint'),
    url(r'^report/8/csv-download$', report_08_streaming_csv_view, name='workery_tenant_report_08_download_csv_file_api_endpoint'),
    url(r'^report/9/csv-download$', report_09_streaming_csv_view, name='workery_tenant_report_09_download_csv_file_api_endpoint'),
    url(r'^report/10/csv-download$', report_10_streaming_csv_view, name='workery_tenant_report_10_download_csv_file_api_endpoint'),
    url(r'^report/12/csv-download$', report_12_streaming_csv_view, name='workery_tenant_report_12_download_csv_file_api_endpoint'),
)
