from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from tenant_report.views.csv.report_01_view import report_01_streaming_csv_view
from tenant_report.views.csv.report_02_view import report_02_streaming_csv_view
from tenant_report.views.csv.report_03_view import report_03_streaming_csv_view
from tenant_report.views.csv.report_04_view import report_04_streaming_csv_view
from tenant_report.views.csv.report_05_view import report_05_streaming_csv_view
from tenant_report.views.csv.report_06_view import report_06_streaming_csv_view
from tenant_report.views.csv.report_07_view import report_07_streaming_csv_view
from tenant_report.views.csv.report_08_view import report_08_streaming_csv_view
from tenant_report.views.csv.report_09_view import report_09_streaming_csv_view
from tenant_report.views.csv.report_10_view import report_10_streaming_csv_view
from tenant_report.views.csv.report_11_view import report_11_streaming_csv_view
from tenant_report.views.csv.report_12_view import report_12_streaming_csv_view
from tenant_report.views.csv.report_13_view import report_13_streaming_csv_view
from tenant_report.views.csv.report_14_view import report_14_streaming_csv_view
from tenant_report.views.csv.report_15_view import report_15_streaming_csv_view
from tenant_report.views.csv.report_16_view import report_16_streaming_csv_view
from tenant_report.views.csv.report_17_view import report_17_streaming_csv_view
from tenant_report.views.csv.report_19_view import report_19_streaming_csv_view
from tenant_report.views.csv.report_20_view import report_20_streaming_csv_view
from tenant_report.views.csv.report_21_view import report_21_streaming_csv_view
from tenant_report.views.csv.report_22_view import report_22_streaming_csv_view
from tenant_report.views.web_views import (
    ReportListView,
    Report01DetailView,
    Report02DetailView,
    Report03DetailView,
    Report04DetailView,
    Report05DetailView,
    Report06DetailView,
    Report07DetailView,
    Report08DetailView,
    Report09DetailView,
    Report10DetailView,
    Report11DetailView,
    Report12DetailView,
    Report13DetailView,
    Report14DetailView,
    Report15DetailView,
    Report16DetailView,
    Report17DetailView
)

urlpatterns = (
    url(r'^reports$', ReportListView.as_view(), name='workery_tenant_reports_list_master'),
    url(r'^report/1/$', Report01DetailView.as_view(), name='workery_tenant_report_01_detail_master'),
    url(r'^report/2/$', Report02DetailView.as_view(), name='workery_tenant_report_02_detail_master'),
    url(r'^report/3/$', Report03DetailView.as_view(), name='workery_tenant_report_03_detail_master'),
    url(r'^report/4/$', Report04DetailView.as_view(), name='workery_tenant_report_04_detail_master'),
    url(r'^report/5/$', Report05DetailView.as_view(), name='workery_tenant_report_05_detail_master'),
    url(r'^report/6/$', Report06DetailView.as_view(), name='workery_tenant_report_06_detail_master'),
    url(r'^report/7/$', Report07DetailView.as_view(), name='workery_tenant_report_07_detail_master'),
    url(r'^report/8/$', Report08DetailView.as_view(), name='workery_tenant_report_08_detail_master'),
    url(r'^report/9/$', Report09DetailView.as_view(), name='workery_tenant_report_09_detail_master'),
    url(r'^report/10/$', Report10DetailView.as_view(), name='workery_tenant_report_10_detail_master'),
    url(r'^report/11/$', Report11DetailView.as_view(), name='workery_tenant_report_11_detail_master'),
    url(r'^report/12/$', Report12DetailView.as_view(), name='workery_tenant_report_12_detail_master'),
    url(r'^report/13/$', Report13DetailView.as_view(), name='workery_tenant_report_13_detail_master'),
    url(r'^report/14/$', Report14DetailView.as_view(), name='workery_tenant_report_14_detail_master'),
    url(r'^report/15/$', Report15DetailView.as_view(), name='workery_tenant_report_15_detail_master'),
    url(r'^report/16/$', Report16DetailView.as_view(), name='workery_tenant_report_16_detail_master'),
    url(r'^report/17/$', Report17DetailView.as_view(), name='workery_tenant_report_17_detail_master'),

    url(r'^report/1/csv-download$', report_01_streaming_csv_view, name='workery_tenant_report_01_download_csv_file_api_endpoint'),
    url(r'^report/2/csv-download$', report_02_streaming_csv_view, name='workery_tenant_report_02_download_csv_file_api_endpoint'),
    url(r'^report/3/csv-download$', report_03_streaming_csv_view, name='workery_tenant_report_03_download_csv_file_api_endpoint'),
    url(r'^report/4/csv-download$', report_04_streaming_csv_view, name='workery_tenant_report_04_download_csv_file_api_endpoint'),
    url(r'^report/5/csv-download$', report_05_streaming_csv_view, name='workery_tenant_report_05_download_csv_file_api_endpoint'),
    url(r'^report/6/csv-download$', report_06_streaming_csv_view, name='workery_tenant_report_06_download_csv_file_api_endpoint'),
    url(r'^report/7/csv-download$', report_07_streaming_csv_view, name='workery_tenant_report_07_download_csv_file_api_endpoint'),
    url(r'^report/8/csv-download$', report_08_streaming_csv_view, name='workery_tenant_report_08_download_csv_file_api_endpoint'),
    url(r'^report/9/csv-download$', report_09_streaming_csv_view, name='workery_tenant_report_09_download_csv_file_api_endpoint'),
    url(r'^report/10/csv-download$', report_10_streaming_csv_view, name='workery_tenant_report_10_download_csv_file_api_endpoint'),
    url(r'^report/11/csv-download$', report_11_streaming_csv_view, name='workery_tenant_report_11_download_csv_file_api_endpoint'),
    url(r'^report/12/csv-download$', report_12_streaming_csv_view, name='workery_tenant_report_12_download_csv_file_api_endpoint'),
    url(r'^report/13/csv-download$', report_13_streaming_csv_view, name='workery_tenant_report_13_download_csv_file_api_endpoint'),
    url(r'^report/14/csv-download$', report_14_streaming_csv_view, name='workery_tenant_report_14_download_csv_file_api_endpoint'),
    url(r'^report/15/csv-download$', report_15_streaming_csv_view, name='workery_tenant_report_15_download_csv_file_api_endpoint'),
    url(r'^report/16/csv-download$', report_16_streaming_csv_view, name='workery_tenant_report_16_download_csv_file_api_endpoint'),
    url(r'^report/17/csv-download$', report_17_streaming_csv_view, name='workery_tenant_report_17_download_csv_file_api_endpoint'),
    url(r'^report/19/csv-download$', report_19_streaming_csv_view, name='workery_tenant_report_19_download_csv_file_api_endpoint'),
    url(r'^report/20/csv-download$', report_20_streaming_csv_view, name='workery_tenant_report_20_download_csv_file_api_endpoint'),
    url(r'^report/21/csv-download$', report_21_streaming_csv_view, name='workery_tenant_report_21_download_csv_file_api_endpoint'),
    url(r'^report/22/csv-download$', report_22_streaming_csv_view, name='workery_tenant_report_22_download_csv_file_api_endpoint'),
)
