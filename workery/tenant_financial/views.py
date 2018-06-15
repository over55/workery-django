# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_foundation.models import WORK_ORDER_STATE, WorkOrder


class UnpaidJobOrderListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        Q(invoice_service_fee_payment_date=None) &
        ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
        ~Q(state=WORK_ORDER_STATE.CANCELLED)
    ).order_by('-id')
    template_name = 'tenant_financial/list/unpaid_view.html'
    paginate_by = 100
    menu_id = "financials"

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unpaid_count'] = WorkOrder.objects.filter(
            Q(invoice_service_fee_payment_date=None) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()

        modified_context['paid_count'] = WorkOrder.objects.filter(
            ~Q(invoice_service_fee_payment_date=None) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()

        modified_context['all_count'] = WorkOrder.objects.filter(
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()

        # Return our modified context.
        return modified_context


class PaidJobOrderListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        ~Q(invoice_service_fee_payment_date=None) &
        ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
        ~Q(state=WORK_ORDER_STATE.CANCELLED)
    ).order_by('-invoice_service_fee_payment_date')
    template_name = 'tenant_financial/list/paid_view.html'
    paginate_by = 100
    menu_id = "financials"

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unpaid_count'] = WorkOrder.objects.filter(
            Q(invoice_service_fee_payment_date=None) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()
        modified_context['paid_count'] = WorkOrder.objects.filter(
            ~Q(invoice_service_fee_payment_date=None) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()
        modified_context['all_count'] = WorkOrder.objects.filter(
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()

        # Return our modified context.
        return modified_context


class AllJobOrderListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = WorkOrder.objects.filter(
        ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
        ~Q(state=WORK_ORDER_STATE.CANCELLED)
    ).order_by('-id')
    template_name = 'tenant_financial/list/all_view.html'
    paginate_by = 100
    menu_id = "financials"

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unpaid_count'] = WorkOrder.objects.filter(
            Q(invoice_service_fee_payment_date=None) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()
        modified_context['paid_count'] = WorkOrder.objects.filter(
            ~Q(invoice_service_fee_payment_date=None) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()
        modified_context['all_count'] = WorkOrder.objects.filter(
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()

        # Return our modified context.
        return modified_context


class JobRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'job_item'
    model = WorkOrder
    template_name = 'tenant_financial/retrieve/view.html'
    menu_id = "financials"

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


class JobUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'job_item'
    model = WorkOrder
    template_name = 'tenant_financial/update/view.html'
    menu_id = "financials"

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
