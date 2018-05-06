# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_foundation.models import ActivitySheetItem, Associate, Customer, TaskItem


@method_decorator(login_required, name='dispatch')
class PendingTaskListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'task_list'
    queryset = TaskItem.objects.filter(is_closed=False)
    template_name = 'tenant_task/pending/list_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Get count of total tasks.
        modified_context['pending_count'] = TaskItem.objects.filter(is_closed=False).count()
        modified_context['closed_count'] = TaskItem.objects.filter(is_closed=True).count()

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class ClosedTaskListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'task_list'
    queryset = TaskItem.objects.filter(is_closed=True)
    template_name = 'tenant_task/closed/list_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Get count of total tasks.
        modified_context['pending_count'] = TaskItem.objects.filter(is_closed=False).count()
        modified_context['closed_count'] = TaskItem.objects.filter(is_closed=True).count()

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/pending/retrieve_view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveForActivitySheetView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/assign/retrieve_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        task_item = modified_context['task_item']

        # STEP 1 - Find all the items belonging to this job and get the `pk` values.
        activity_sheet_associate_pks = ActivitySheetItem.objects.filter(
           order=task_item.job
        ).values_list('associate_id', flat=True)

        # STEP 2 -
        # (a) Find all the unique associates that match the job skill criteria
        #     for the job.
        # (b) Find all the unique associates which do not have any activity
        #     sheet items created previously.
        skill_set_pks = task_item.job.skill_sets.values_list('pk', flat=True)
        available_associates = Associate.objects.filter(
           Q(skill_sets__in=skill_set_pks) &
           ~Q(id__in=activity_sheet_associate_pks)
        ).distinct()
        modified_context['available_associates_list'] = available_associates

        # STEP 3 - Fetch all the activity sheets we already have
        modified_context['existing_activity_sheet'] = ActivitySheetItem.objects.filter(
           order=task_item.job
        )

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveForActivitySheetAndAssignAssociateCreateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/assign/create_view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveAndUnassignCreateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/unassign/create_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveAndCloseCreateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/close/create_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveAndPostponeCreateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/postpone/create_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PendingTaskRetrieveAndCompleteCreateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'task_item'
    model = TaskItem
    template_name = 'tenant_task/component/complete/create_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Return our modified context.
        return modified_context
