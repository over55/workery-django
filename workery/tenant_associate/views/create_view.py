# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import (
    Associate,
    InsuranceRequirement,
    SkillSet,
    Tag,
    VehicleType
)


class MemberCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_associate/create/create_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = "associates" # Required for navigation
        modified_context['insurance_requirements'] = InsuranceRequirement.objects.all()
        modified_context['tags'] = Tag.objects.all()
        modified_context['skill_sets'] = SkillSet.objects.all()
        modified_context['vehicle_types'] = VehicleType.objects.all()
        return modified_context


class MemberConfirmCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_associate/create/confirm_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = "associates" # Required for navigation
        return modified_context
