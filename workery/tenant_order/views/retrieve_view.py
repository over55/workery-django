# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, FormView, UpdateView

from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    GroupRequiredMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.order import WorkOrderFilter
from tenant_foundation.models import (
    ActivitySheetItem,
    Associate,
    Customer,
    WorkOrder,
    WORK_ORDER_STATE,
    SkillSet,
    TaskItem
)


class JobLiteRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/lite_view.html'
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
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        job = modified_context['job']


        # Return our modified context.
        return modified_context


class JobFullRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/full_view.html'
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


class JobRetrieveForActivitySheetListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/activity_sheet_list_view.html'
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

        # Fetch all the activity sheets we already have
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(
           job=modified_context['job']
        )

        # Return our modified context.
        return modified_context


class JobRetrieveForTasksListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/task_list_view.html'
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

        # Fetch all the activity sheets we already have
        modified_context['task_items'] = TaskItem.objects.filter(
           job=modified_context['job']
        ).order_by('-last_modified_at')

        # Return our modified context.
        return modified_context


class JobRetrieveForCommentsListAndCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/comments_view.html'
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
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
    

class JobRetrieveForFilesListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/files_view.html'
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
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class ArchivedJobFullRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = WorkOrder
    template_name = 'tenant_order/retrieve/for/archive_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
