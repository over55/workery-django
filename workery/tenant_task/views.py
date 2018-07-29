# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    GroupRequiredMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.task_item import TaskItemFilter
from tenant_foundation.constants import *
from tenant_foundation.models import ActivitySheetItem, Associate, AwayLog, Customer, TaskItem


class PendingTaskListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'task_list'
    template_name = 'tenant_task/pending/list_view.html'
    paginate_by = 100
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        """
        Override the `get_queryset` function to include context based filtering.
        """
        queryset = TaskItem.objects.filter(
            is_closed=False
        ).prefetch_related(
            'job',
            'job__associate',
            'job__customer',
            'created_by',
            'last_modified_by'
        )

        # Filter out management staff restricted tasks from being loaded.
        if not self.request.user.is_executive() and not self.request.user.is_management_staff():
            queryset = queryset.exclude(type_of=UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID)

        return queryset

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unassigned_count'] = TaskItem.objects.filter(job__associate=None, is_closed=False).count()
        modified_context['pending_count'] = TaskItem.objects.filter(is_closed=False).count()
        modified_context['closed_count'] = TaskItem.objects.filter(is_closed=True).count()

        # Return our modified context.
        return modified_context


class ClosedTaskListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'task_list'
    template_name = 'tenant_task/closed/list_view.html'
    paginate_by = 100
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        """
        Override the `get_queryset` function to include context based filtering.
        """
        queryset = TaskItem.objects.filter(
            is_closed=True
        ).prefetch_related(
            'job',
            'job__associate',
            'job__customer',
            'created_by',
            'last_modified_by'
        )

        # Filter out management staff restricted tasks from being loaded.
        if not self.request.user.is_executive() and not self.request.user.is_management_staff():
            queryset = queryset.exclude(type_of=UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID)

        return queryset

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unassigned_count'] = TaskItem.objects.filter(job__associate=None, is_closed=False).count()
        modified_context['pending_count'] = TaskItem.objects.filter(is_closed=False).count()
        modified_context['closed_count'] = TaskItem.objects.filter(is_closed=True).count()

        # Return our modified context.
        return modified_context


class PendingTaskRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/pending/retrieve_view.html'
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Defensive Code - Prevent access to detail if already closed.
        task_item = modified_context['task_item']
        if task_item.is_closed:
            print(task_item)
            raise Http404("Task was already closed!")

        # Return our modified context.
        return modified_context


class PendingTaskRetrieveForActivitySheetView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/assign/retrieve_view.html'
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        task_item = modified_context['task_item']

        # Defensive Code - Prevent access to detail if already closed.
        task_item = modified_context['task_item']
        if task_item.is_closed:
            print(task_item)
            raise Http404("Task was already closed!")

        # STEP 1 - Find all the items belonging to this job and get the `pk` values.
        activity_sheet_associate_pks = ActivitySheetItem.objects.filter(
           job=task_item.job
        ).values_list('associate_id', flat=True)

        # STEP 2 -
        # (a) Find all the unique associates that match the job skill criteria
        #     for the job.
        # (b) Find all the unique associates which do not have any activity
        #     sheet items created previously.
        # (c) FInd all unique associates which have active accounts.
        # (d) If an Associate has an active Announcement attached to them,
        #     they should be uneligible for a job.
        skill_set_pks = task_item.job.skill_sets.values_list('pk', flat=True)
        available_associates = Associate.objects.filter(
           Q(skill_sets__in=skill_set_pks) &
           ~Q(id__in=activity_sheet_associate_pks) &
           Q(owner__is_active=True) &
           Q(away_log__isnull=True)
        ).distinct()
        modified_context['available_associates_list'] = available_associates

        # STEP 3 - Fetch all the activity sheets we already have
        modified_context['existing_activity_sheet'] = ActivitySheetItem.objects.filter(
           job=task_item.job
        )

        # Return our modified context.
        return modified_context


class PendingTaskRetrieveForActivitySheetAndAssignAssociateCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/assign/create_view.html'
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        task_item = modified_context['task_item']

        # Defensive Code - Prevent access to detail if already closed.
        task_item = modified_context['task_item']
        if task_item.is_closed:
            print(task_item)
            raise Http404("Task was already closed!")

        # Return our modified context.
        return modified_context


class PendingTaskRetrieveAndCompleteCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/complete/create_view.html'
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        task_item = modified_context['task_item']

        # Defensive Code - Prevent access to detail if already closed.
        task_item = modified_context['task_item']
        if task_item.is_closed:
            print(task_item)
            raise Http404("Task was already closed!")

        # Return our modified context.
        return modified_context


class UnassignedTaskListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'task_list'
    queryset = TaskItem.objects.filter(
        job__associate=None,
        is_closed=False
    ).prefetch_related(
        'job',
        'job__associate',
        'job__customer',
        'created_by',
        'last_modified_by'
    )
    template_name = 'tenant_task/unassigned/list_view.html'
    paginate_by = 100
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Get count of total tasks.
        modified_context['unassigned_count'] = TaskItem.objects.filter(job__associate=None, is_closed=False).count()
        modified_context['pending_count'] = TaskItem.objects.filter(is_closed=False).count()
        modified_context['closed_count'] = TaskItem.objects.filter(is_closed=True).count()

        # Return our modified context.
        return modified_context


class PendingTaskRetrieveForActivityFollowUpWithAssociateSheetView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/pending_follow_up/create_view.html'
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class TaskSearchView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_task/search/search_view.html'
    menu_id = "task"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class TaskSearchResultView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'task_list'
    queryset = TaskItem.objects.order_by('-created')
    template_name = 'tenant_task/search/result_view.html'
    paginate_by = 100
    menu_id = "task"
    skip_parameters_array = ['page']
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        # Run our search query.
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = TaskItem.objects.full_text_search(keyword)
        else:
            queryset = super(TaskSearchResultView, self).get_queryset()
            filter = TaskItemFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related(
            'job',
            'job__associate',
            'job__customer',
            'created_by',
            'last_modified_by'
        )

        # Check what template we are in and filter accordingly.
        template = self.kwargs['template']
        if template == 'pending':
            queryset = queryset.filter(is_closed=False)
        else:
            queryset = queryset.filter(is_closed=True)

        # Return the results filtered
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['pending',]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
