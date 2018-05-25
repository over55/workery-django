# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer


class CustomerSummaryView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'customer_list'
    template_name = 'tenant_customer/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "customers"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-id')
        return queryset


class CustomerListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'customer_list'
    template_name = 'tenant_customer/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers" # Required for navigation
        return context

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('given_name', 'last_name')

        # The following code will use the 'django-filter'
        filter = CustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset
