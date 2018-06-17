# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView
)
from tenant_api.filters.order import WorkOrderFilter
from tenant_foundation.models import WorkOrder, WORK_ORDER_STATE


class JobSummaryView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        ~Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID) &
        ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
        ~Q(state=WORK_ORDER_STATE.CANCELLED)
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_order/summary/view.html'
    paginate_by = 100
    menu_id = 'jobs'


class JobListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.exclude(
        state=WORK_ORDER_STATE.ARCHIVED
    ).order_by('-id')
    template_name = 'tenant_order/list/view.html'
    paginate_by = 100
    menu_id = 'jobs'

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


class ArchivedJobListView(LoginRequiredMixin, WorkeryListView):
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
