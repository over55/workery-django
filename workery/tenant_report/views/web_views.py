# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
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


@method_decorator(login_required, name='dispatch')
class ReportListView(TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/list_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


@method_decorator(login_required, name='dispatch')
class Report07DetailView(TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_07_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


@method_decorator(login_required, name='dispatch')
class Report08DetailView(TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_08_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context


@method_decorator(login_required, name='dispatch')
class Report09DetailView(TemplateView, ExtraRequestProcessingMixin):
    template_name = 'tenant_report/report_09_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = 'reports' # Required
        return modified_context
