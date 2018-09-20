# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
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
from tenant_foundation.models import WORK_ORDER_STATE, WorkOrder, WorkOrderServiceFee


class UnpaidJobOrderListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
    ).order_by('-id').prefetch_related(
        'customer',
        'associate',
    )
    template_name = 'tenant_financial/list/unpaid_view.html'
    paginate_by = 100
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unpaid_count'] = WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID).count()
        modified_context['paid_count'] = WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID).count()
        modified_context['all_count'] = WorkOrder.objects.filter(
            Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID) |
            Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)
        ).count()

        # Added boolean to view based on whether user is in management.
        modified_context['user_is_management_or_executive_staff'] = self.request.user.is_management_or_executive_staff()

        # Return our modified context.
        return modified_context


class PaidJobOrderListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        state=WORK_ORDER_STATE.COMPLETED_AND_PAID
    ).order_by('-invoice_service_fee_payment_date').prefetch_related(
        'customer',
        'associate',
    )
    template_name = 'tenant_financial/list/paid_view.html'
    paginate_by = 100
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unpaid_count'] = WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID).count()
        modified_context['paid_count'] = WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID).count()
        modified_context['all_count'] = WorkOrder.objects.filter(
            Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID) |
            Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)
        ).count()

        # Added boolean to view based on whether user is in management.
        modified_context['user_is_management_or_executive_staff'] = self.request.user.is_management_or_executive_staff()

        # Return our modified context.
        return modified_context


class AllJobOrderListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID) |
        Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)
    ).order_by('-id').prefetch_related(
        'customer',
        'associate',
    )
    template_name = 'tenant_financial/list/all_view.html'
    paginate_by = 100
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unpaid_count'] = WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID).count()
        modified_context['paid_count'] = WorkOrder.objects.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID).count()
        modified_context['all_count'] = WorkOrder.objects.filter(
            Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID) |
            Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)
        ).count()

        # Added boolean to view based on whether user is in management.
        modified_context['user_is_management_or_executive_staff'] = self.request.user.is_management_or_executive_staff()

        # Return our modified context.
        return modified_context


class JobRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job_item'
    model = WorkOrder
    template_name = 'tenant_financial/retrieve/view.html'
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['unpaid-jobs', 'paid-jobs', 'all-jobs']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class JobUpdateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job_item'
    model = WorkOrder
    template_name = 'tenant_financial/update/view.html'
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['unpaid-jobs', 'paid-jobs', 'all-jobs']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Attach all the service fees.
        modified_context['service_fees'] = WorkOrderServiceFee.objects.all()

        # Return our modified context.
        return modified_context



class WorkOrderSearchView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_financial/search/search_view.html'
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]


class WorkOrderSearchResultView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'order_list'
    queryset = WorkOrder.objects.order_by('-created')
    template_name = 'tenant_financial/search/result_view.html'
    paginate_by = 100
    menu_id = "financials"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]
    skip_parameters_array = ['page']

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        # Run our search query.
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = WorkOrder.objects.full_text_search(keyword)
        else:
            queryset = super(WorkOrderSearchResultView, self).get_queryset()
            filter = WorkOrderFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related('customer', 'associate',)

        # Check what template we are in and filter accordingly.
        template = self.kwargs['template']
        if template == 'unpaid-jobs':
            queryset = queryset.filter(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID)
        if template == 'paid-jobs':
            queryset = queryset.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)

        # Return the results filtered
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['unpaid-jobs','paid-jobs',]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
