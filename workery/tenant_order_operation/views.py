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
