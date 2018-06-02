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
from tenant_api.filters.partner import PartnerFilter
from tenant_foundation.models import (
    Partner,
    SkillSet,
    Tag
)


class PartnerCreateView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_partner/create/create_view.html'
    menu_id = "partners"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['skill_sets'] = SkillSet.objects.all()
        return context


class PartnerConfirmCreateView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_partner/create/confirm_view.html'
    menu_id = "partners"
