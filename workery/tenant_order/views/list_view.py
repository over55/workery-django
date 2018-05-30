# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_foundation.models.order import Order


class JobSummaryView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.filter(
        is_cancelled=False,
        completion_date__isnull=True,
        invoice_service_fee_payment_date__isnull=True,
        is_archived=False
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_order/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class JobListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.filter(is_archived=True).order_by('-id')
    template_name = 'tenant_order/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs" # Required for navigation
        return context

    def get_queryset(self):
        queryset = super(JobListView, self).get_queryset() # Get the base.

        # The following code will use the 'django-filter'
        filter = OrderFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        queryset = queryset.filter(is_archived=False)
        queryset = queryset.prefetch_related('customer', 'associate')
        return queryset


class ArchivedJobListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.filter(
        is_archived=True
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_order/list/archived_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context
