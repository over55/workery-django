# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
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
from tenant_foundation.models import (
    Staff,
    SkillSet,
    Tag,
    ResourceCategory,
    ResourceItem,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    WorkOrderServiceFee
)


class RunningOrInactiveOngoingJobListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = OngoingWorkOrder.objects.filter(
        Q(state=ONGOING_WORK_ORDER_STATE.RUNNING) |
        Q(state=ONGOING_WORK_ORDER_STATE.IDLE)
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_ongoing_order/list/running_or_inactive_view.html'
    paginate_by = 100
    menu_id = 'ongoing-jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        modified_context['running_or_inactivate_jobs_count'] = OngoingWorkOrder.objects.filter(
            Q(state=ONGOING_WORK_ORDER_STATE.RUNNING) |
            Q(state=ONGOING_WORK_ORDER_STATE.IDLE)
        ).count()
        modified_context['terminated_jobs_count'] = OngoingWorkOrder.objects.filter(
            state=ONGOING_WORK_ORDER_STATE.TERMINATED
        ).count()

        # Return our modified context.
        return modified_context

class TerminatedOngoingJobListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = OngoingWorkOrder.objects.filter(
        state=ONGOING_WORK_ORDER_STATE.TERMINATED
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_ongoing_order/list/terminated_view.html'
    paginate_by = 100
    menu_id = 'ongoing-jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        modified_context['running_or_inactivate_jobs_count'] = OngoingWorkOrder.objects.filter(
            Q(state=ONGOING_WORK_ORDER_STATE.RUNNING) |
            Q(state=ONGOING_WORK_ORDER_STATE.IDLE)
        ).count()
        modified_context['terminated_jobs_count'] = OngoingWorkOrder.objects.filter(
            state=ONGOING_WORK_ORDER_STATE.TERMINATED
        ).count()

        # Return our modified context.
        return modified_context


class OngoingJobLiteRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/retrieve/lite_view.html'
    menu_id = 'ongoing-jobs'
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
        if template not in ['search', 'summary', 'list',]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class OngoingJobFullRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/retrieve/full_view.html'
    menu_id = 'ongoing-jobs'
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

        # Get sorted values.
        job = modified_context['job']
        modified_context['ordered_closed_jobs'] = job.closed_orders.order_by('-id')

        # Return our modified context.
        return modified_context




class OngoingJobRetrieveForCommentsListAndCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/retrieve/for/comments_view.html'
    menu_id = 'ongoing-jobs'
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
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class OngoingJobUpdateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/update/view.html'
    menu_id = 'ongoing-jobs'
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
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Set our dependencies
        modified_context['skillsets'] = SkillSet.objects.all().order_by('sub_category')
        modified_context['servicefees'] = WorkOrderServiceFee.objects.all()

        # Return our modified context.
        return modified_context
