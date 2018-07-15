# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    WorkOrder,
    TaskItem
)


class ReportListView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/list_view.html'
    menu_id = "reports"


class Report01DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_01_view.html'
    menu_id = "reports"


class Report05DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_05_view.html'
    menu_id = "reports"


class Report06DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_06_view.html'
    menu_id = "reports"


class Report07DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_07_view.html'
    menu_id = "reports"


class Report08DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_08_view.html'
    menu_id = "reports"


class Report09DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_09_view.html'
    menu_id = "reports"


class Report10DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_10_view.html'
    menu_id = "reports"


class Report12DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_12_view.html'
    menu_id = "reports"


class Report13DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_13_view.html'
    menu_id = "reports"


class Report14DetailView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_report/report_14_view.html'
    menu_id = "reports"
