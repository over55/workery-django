# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_foundation.models import ActivitySheetItem, Associate, Customer, Order, SkillSet, TaskItem


class JobLiteRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/lite_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class JobFullRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/full_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class JobRetrieveForActivitySheetListView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/activity_sheet_list_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Fetch all the activity sheets we already have
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(
           job=modified_context['job']
        )

        # Return our modified context.
        return modified_context


class JobRetrieveForTasksListView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/task_list_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Fetch all the activity sheets we already have
        modified_context['task_items'] = TaskItem.objects.filter(
           job=modified_context['job']
        ).order_by('-last_modified_at')

        # Return our modified context.
        return modified_context


class JobRetrieveForCommentsListAndCreateView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/comments_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class JobRetrieveForCloseCreateView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/close_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class JobRetrieveForPostponeCreateView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/postpone_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class JobRetrieveForUnassignCreateView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/unassign_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class ArchivedJobFullRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/for/archive_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context
