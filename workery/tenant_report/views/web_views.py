# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    Order,
    TaskItem
)


class ReportListView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/list_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report01DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_01_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report05DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_05_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report06DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_06_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report07DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_07_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report08DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_08_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report09DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_09_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report10DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_10_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


class Report12DetailView(LoginRequiredMixin, TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_12_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context
