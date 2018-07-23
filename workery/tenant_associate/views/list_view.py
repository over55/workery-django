# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    GroupRequiredMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import Associate


#---------#
# SUMMARY #
#---------#


class MemberSummaryView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'associate_list'
    template_name = 'tenant_associate/summary/view.html'
    paginate_by = 100
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Associate.objects.filter(
            owner__is_active=True
        ).prefetch_related(
            'owner'
        ).order_by('-id')
        return queryset


#------#
# LIST #
#------#


class MemberListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'associate_list'
    template_name = 'tenant_associate/list/view.html'
    paginate_by = 100
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Associate.objects.order_by(
            'given_name',
            'last_name'
        ).prefetch_related('owner')
        return queryset
