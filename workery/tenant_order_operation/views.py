# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView,
    GroupRequiredMixin,
    ReturnIDParameterRequiredMixin
)
from tenant_api.filters.order import WorkOrderFilter
from tenant_foundation.models import ActivitySheetItem, Associate, Customer, WorkOrder, SkillSet, TaskItem


class CompletedWorkOrderUnassignOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order_operation/completed_work_order_unassign_operation.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]
    return_id_required = ['financials-pending']


class CompletedWorkOrderCloseOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order_operation/completed_work_order_close_operation.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]
    return_id_required = ['financials-pending']


class CompletedWorkOrderCancelOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order_operation/completed_work_order_cancel_operation.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID
    ]
    return_id_required = ['financials-pending']


class IncompletedWorkOrderUnassignOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order_operation/incompleted_work_order_unassign_operation.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']


class JobRetrieveForCloseCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/close_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context



class JobRetrieveForPostponeCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/postpone_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class JobRetrieveForReopeningCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/reopen_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class TransferWorkOrderOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order_operation/transfer_work_order_operation.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']
