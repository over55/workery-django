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
from tenant_foundation.models import (
    ActivitySheetItem,
    Associate,
    OngoingWorkOrder
)


class OngoingWorkOrderAssignOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'ongoing_job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/assign_part_1_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        ongoing_job = modified_context['ongoing_job']

        # # Defensive Code - Prevent access to detail if already closed.
        # task_item = modified_context['task_item']
        # if task_item.is_closed:
        #     raise Http404("Task was already closed!")

        # STEP 1 - Find all the items belonging to this job and get the `pk` values.
        activity_sheet_associate_pks =  ActivitySheetItem.objects.filter(ongoing_job=ongoing_job).values_list('associate_id', flat=True)

        # STEP 2 -
        # (a) Find all the unique associates that match the job skill criteria
        #     for the job.
        # (b) Find all the unique associates which do not have any activity
        #     sheet items created previously.
        # (c) FInd all unique associates which have active accounts.
        # (d) If an Associate has an active Announcement attached to them,
        #     they should be uneligible for a job.
        skill_set_pks = ongoing_job.skill_sets.values_list('pk', flat=True)

        available_associates = Associate.objects.filter(
           Q(skill_sets__in=skill_set_pks) &
           ~Q(id__in=activity_sheet_associate_pks) &
           Q(owner__is_active=True) &
           Q(away_log__isnull=True)
        ).distinct()
        modified_context['available_associates_list'] = available_associates

        # STEP 3 - Fetch all the activity sheets we already have
        modified_context['existing_activity_sheet'] = ActivitySheetItem.objects.filter(
           ongoing_job=ongoing_job
        )

        # Return our modified context.
        return modified_context


class OngoingWorkOrderAssignConfirmOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'ongoing_job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/assign_part_2_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Defensive Code - Prevent access to detail if already closed.
        ongoing_job = modified_context['ongoing_job']
        # if task_item.is_closed:
        #     print(task_item)
        #     raise Http404("Task was already closed!")

        # Return our modified context.
        return modified_context


class OngoingWorkOrderUnassignOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'ongoing_job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/unassign_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']


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
    return_id_required = ['lite-retrieve', 'pending-task']


class OngoingWorkOrderCreationWizardOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'ongoing_job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/creation_wizard.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve',]


class OngoingWorkOrderFollowUpOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'ongoing_job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/follow_up.html'
    menu_id = 'ongoing_job'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']



#TODO: PendingFollowUpOperation



class OngoingWorkOrderCompletionSurveyOperationView(LoginRequiredMixin, GroupRequiredMixin, ReturnIDParameterRequiredMixin, WorkeryDetailView):
    context_object_name = 'ongoing_job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order_operation/completion_survey.html'
    menu_id = 'ongoing_job'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
    return_id_required = ['lite-retrieve', 'pending-task']
