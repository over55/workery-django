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
from tenant_foundation.models import OngoingWorkOrder


class OngoingWorkOrderUnassignOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/unassign_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve']


class OngoingWorkOrderCloseOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/close_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve']
