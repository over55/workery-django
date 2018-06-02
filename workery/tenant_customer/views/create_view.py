# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Customer,
    SkillSet,
    Tag
)


class PickCustomerTypeInCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_customer/create/pick_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "customers" # Required for navigation
        return context


class ResidentialCustomerCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_customer/create/residential_create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "customers" # Required for navigation
        context['tags'] = Tag.objects.all()
        context['skill_sets'] = SkillSet.objects.all()
        return context


class ResidentialCustomerConfirmCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_customer/create/residential_confirm_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "customers" # Required for navigation
        return context


class CommercialCustomerCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_customer/create/commercial_create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "customers" # Required for navigation
        context['tags'] = Tag.objects.all()
        context['skill_sets'] = SkillSet.objects.all()
        return context


class CommercialCustomerConfirmCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_customer/create/commercial_confirm_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "customers" # Required for navigation
        return context
