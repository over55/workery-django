# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer, WorkOrder


class CustomerLiteRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/lite_view.html'
    menu_id = 'customers'

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


class CustomerFullRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/full_view.html'
    menu_id = 'customers'

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


class CustomerRetrieveForCommentListAndCreateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/for/comments_view.html'
    menu_id = 'customers'

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


class CustomerRetrieveForJobsListView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/retrieve/for/jobs_view.html'
    menu_id = 'customers'

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
        modified_context['jobs'] = WorkOrder.objects.filter(
            customer = modified_context['customer']
        )

        # Return our modified context.
        return modified_context
