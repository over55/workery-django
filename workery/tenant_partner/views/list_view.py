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
from tenant_foundation.models import Partner


#---------#
# SUMMARY #
#---------#


class PartnerSummaryView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'partner_list'
    template_name = 'tenant_partner/summary/view.html'
    paginate_by = 100
    menu_id = "partners"

    def get_queryset(self):
        queryset = Partner.objects.filter(owner__is_active=True).order_by('-id').prefetch_related(
            'owner',
        )
        return queryset


#------#
# LIST #
#------#


class PartnerListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'partner_list'
    template_name = 'tenant_partner/list/view.html'
    paginate_by = 100
    menu_id = "partners"

    def get_queryset(self):
        queryset = Partner.objects.order_by('given_name', 'last_name').prefetch_related(
            'owner',
        )
        return queryset
