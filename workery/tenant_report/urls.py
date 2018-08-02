from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_report.views.csv.report_01_view import report_01_streaming_csv_view
from tenant_report.views.csv.report_02_view import report_02_streaming_csv_view
from tenant_report.views.csv.report_03_view import report_03_streaming_csv_view
from tenant_report.views.web_views import (
    ReportListView,
    Report01DetailView,
    Report02DetailView,
    Report03DetailView,
    Report06DetailView,
    Report07DetailView,
    Report08DetailView,
    Report09DetailView,
    Report10DetailView,
    Report12DetailView,
    Report13DetailView,
    Report14DetailView,
)
from tenant_report.views.csv_views import (
    report_06_streaming_csv_view,
    report_07_streaming_csv_view,
    report_08_streaming_csv_view,
    report_09_streaming_csv_view,
    report_10_streaming_csv_view,
    report_12_streaming_csv_view,
    report_13_streaming_csv_view,
    report_14_streaming_csv_view,
)

urlpatterns = (
    url(r'^reports$', ReportListView.as_view(), name='workery_tenant_reports_list_master'),
    url(r'^report/1/$', Report01DetailView.as_view(), name='workery_tenant_report_01_detail_master'),
    url(r'^report/2/$', Report02DetailView.as_view(), name='workery_tenant_report_02_detail_master'),
    url(r'^report/3/$', Report03DetailView.as_view(), name='workery_tenant_report_03_detail_master'),
    url(r'^report/6/$', Report06DetailView.as_view(), name='workery_tenant_report_06_detail_master'),
    url(r'^report/7/$', Report07DetailView.as_view(), name='workery_tenant_report_07_detail_master'),
    url(r'^report/8/$', Report08DetailView.as_view(), name='workery_tenant_report_08_detail_master'),
    url(r'^report/9/$', Report09DetailView.as_view(), name='workery_tenant_report_09_detail_master'),
    url(r'^report/10/$', Report10DetailView.as_view(), name='workery_tenant_report_10_detail_master'),
    url(r'^report/12/$', Report12DetailView.as_view(), name='workery_tenant_report_12_detail_master'),
    url(r'^report/13/$', Report13DetailView.as_view(), name='workery_tenant_report_13_detail_master'),
    url(r'^report/14/$', Report14DetailView.as_view(), name='workery_tenant_report_14_detail_master'),

    url(r'^report/1/csv-download$', report_01_streaming_csv_view, name='workery_tenant_report_01_download_csv_file_api_endpoint'),
    url(r'^report/2/csv-download$', report_02_streaming_csv_view, name='workery_tenant_report_02_download_csv_file_api_endpoint'),
    url(r'^report/3/csv-download$', report_03_streaming_csv_view, name='workery_tenant_report_03_download_csv_file_api_endpoint'),
    url(r'^report/6/csv-download$', report_06_streaming_csv_view, name='workery_tenant_report_06_download_csv_file_api_endpoint'),
    url(r'^report/7/csv-download$', report_07_streaming_csv_view, name='workery_tenant_report_07_download_csv_file_api_endpoint'),
    url(r'^report/8/csv-download$', report_08_streaming_csv_view, name='workery_tenant_report_08_download_csv_file_api_endpoint'),
    url(r'^report/9/csv-download$', report_09_streaming_csv_view, name='workery_tenant_report_09_download_csv_file_api_endpoint'),
    url(r'^report/10/csv-download$', report_10_streaming_csv_view, name='workery_tenant_report_10_download_csv_file_api_endpoint'),
    url(r'^report/12/csv-download$', report_12_streaming_csv_view, name='workery_tenant_report_12_download_csv_file_api_endpoint'),
    url(r'^report/13/csv-download$', report_13_streaming_csv_view, name='workery_tenant_report_13_download_csv_file_api_endpoint'),
    url(r'^report/14/csv-download$', report_14_streaming_csv_view, name='workery_tenant_report_14_download_csv_file_api_endpoint'),
)
