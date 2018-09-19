# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.views.generic.edit import CreateView, FormView, UpdateView
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
from tenant_api.filters.order import WorkOrderFilter
from tenant_foundation.models import WorkOrder, WorkOrderComment, WORK_ORDER_STATE


class JobSummaryView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        Q(state=WORK_ORDER_STATE.NEW) |
        Q(state=WORK_ORDER_STATE.IN_PROGRESS) |
        Q(state=WORK_ORDER_STATE.DECLINED)
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_order/summary/view.html'
    paginate_by = 100
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Check user role permission.
        modified_context['user_is_in_management'] = False
        if self.request.user.is_executive() or self.request.user.is_management_staff():
            modified_context['user_is_in_management'] = True

        # Return our modified context.
        return modified_context


class JobListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.exclude(
        state=WORK_ORDER_STATE.ARCHIVED
    ).order_by('-id')
    template_name = 'tenant_order/list/view.html'
    paginate_by = 100
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = super(JobListView, self).get_queryset() # Get the base.

        # The following code will use the 'django-filter'
        filter = WorkOrderFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        queryset = queryset.exclude(
            state=WORK_ORDER_STATE.ARCHIVED
        )
        queryset = queryset.prefetch_related('customer', 'associate')
        return queryset


    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Check user role permission.
        modified_context['user_is_in_management'] = False
        if self.request.user.is_executive() or self.request.user.is_management_staff():
            modified_context['user_is_in_management'] = True

        # Return our modified context.
        return modified_context


class ArchivedJobListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        state=WORK_ORDER_STATE.ARCHIVED
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_order/list/archived_view.html'
    paginate_by = 100
    menu_id = 'jobs'
    skip_parameters_array = ['page']
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class JobCommentsListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'comments_list'
    queryset = WorkOrderComment.objects.order_by(
        '-created_at'
    ).prefetch_related(
        'about',
        'comment'
    )
    template_name = 'tenant_order/list/job_comments_view.html'
    paginate_by = 100
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = super(JobCommentsListView, self).get_queryset() # Get the base.
        return queryset
