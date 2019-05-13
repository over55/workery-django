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
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import Staff


#---------#
# SUMMARY #
#---------#


class TeamSummaryView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'staff_list'
    template_name = 'tenant_team/summary/view.html'
    paginate_by = 100
    menu_id = "team"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Staff.objects.filter(
            owner__is_active=True
        ).order_by(
            'last_name',
            'given_name',
        ).prefetch_related(
            'owner',
        )
        # The following code will use the 'django-filter'
        filter = StaffFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


#------#
# LIST #
#------#


class TeamListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'staff_list'
    template_name = 'tenant_team/list/view.html'
    paginate_by = 100
    menu_id = "team"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Staff.objects.all().order_by(
            'last_name',
            'given_name',
        )

        # The following code will use the 'django-filter'
        filter = StaffFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        queryset = queryset.prefetch_related(
            'owner',
        )
        return queryset
