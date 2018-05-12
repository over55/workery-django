# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.partner import PartnerFilter
from tenant_foundation.models import (
    Partner,
    SkillSet,
    Tag
)


@method_decorator(login_required, name='dispatch')
class PartnerCreateView(TemplateView):
    template_name = 'tenant_partner/create/create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "partners" # Required for navigation
        context['tags'] = Tag.objects.all()
        context['skill_sets'] = SkillSet.objects.all()
        return context


@method_decorator(login_required, name='dispatch')
class PartnerConfirmCreateView(TemplateView):
    template_name = 'tenant_partner/create/confirm_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "partners" # Required for navigation
        return context
