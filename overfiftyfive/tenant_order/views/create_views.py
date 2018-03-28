# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_foundation.models.order import Order


@method_decorator(login_required, name='dispatch')
class Step1CreateOrAddCustomerView(TemplateView):
    template_name = 'tenant_order/create/step_1_search_or_add_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs" # Required for navigation
        return context


@method_decorator(login_required, name='dispatch')
class Step1CustomerSearchResultsView(TemplateView):
    template_name = 'tenant_order/create/step_1_search_results_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class Step1AddCustomerView(TemplateView):
    template_name = 'tenant_order/create/step_1_create_customer_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class Step1AddCustomerConfirmationView(TemplateView):
    template_name = 'tenant_order/create/step_1_create_customer_confirmation_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class Step2View(TemplateView):
    template_name = 'tenant_order/create/step_2_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class Step3View(TemplateView):
    template_name = 'tenant_order/create/step_3_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class Step4View(TemplateView):
    template_name = 'tenant_order/create/step_4_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class Step5View(TemplateView):
    template_name = 'tenant_order/create/step_5_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context
