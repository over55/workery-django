# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
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
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer, WorkOrder


class CustomerLiteRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/lite_view.html'
    menu_id = 'customers'
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


class CustomerFullRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/full_view.html'
    menu_id = 'customers'
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


class CustomerRetrieveForCommentListAndCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/for/comments_view.html'
    menu_id = 'customers'
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


class CustomerRetrieveForJobsListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/for/jobs_view.html'
    menu_id = 'customers'
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

        # Added boolean to view based on whether user is in management.
        modified_context['user_is_management_or_executive_staff'] = self.request.user.is_management_or_executive_staff()

        # Required for navigation
        modified_context['jobs'] = WorkOrder.objects.filter(
            customer = modified_context['customer']
        ).order_by('-completion_date')

        # Return our modified context.
        return modified_context
