# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer


#--------#
# CREATE #
#--------#

@method_decorator(login_required, name='dispatch')
class CustomerCreateView(TemplateView):
    template_name = 'tenant_customer/create/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers" # Required for navigation
        return context


#---------#
# SUMMARY #
#---------#


@method_decorator(login_required, name='dispatch')
class CustomerSummaryView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_customer/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers" # Required for navigation
        return context

    def get_queryset(self):
        queryset = Customer.objects.all()
        queryset = queryset.order_by('-created')
        return queryset


#------#
# LIST #
#------#


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_customer/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers" # Required for navigation
        return context

    def get_queryset(self):
        queryset = super(CustomerListView, self).get_queryset() # Get the base.

        # The following code will use the 'django-filter'
        filter = CustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


#--------#
# SEARCH #
#--------#


@method_decorator(login_required, name='dispatch')
class CustomerSearchView(TemplateView):
    template_name = 'tenant_customer/search/search_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers"
        return context


@method_decorator(login_required, name='dispatch')
class CustomerSearchResultView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_customer/search/result_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "customers"

        # DEVELOPERS NOTE:
        # - This class based view will have URL parameters for filtering and
        #   searching records.
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['filter_parameters'] = self.get_param_urls(['page'])

        # Return our modified context.
        return modified_context

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = Customer.objects.full_text_search(keyword)
            queryset = queryset.order_by('-created')
        else:
            queryset = super(CustomerListView, self).get_queryset()

        # The following code will use the 'django-filter'
        filter = CustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


#----------#
# RETRIEVE #
#----------#


@method_decorator(login_required, name='dispatch')
class CustomerRetrieveView(DetailView):
    model = Customer
    template_name = 'tenant_customer/retrieve/view.html'

    def get_object(self):
        customer = super().get_object()  # Call the superclass
        return customer                  # Return the object

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
        modified_context['current_page'] = "customers"

        # Return our modified context.
        return modified_context


#----------#
# UPDATE #
#----------#


@method_decorator(login_required, name='dispatch')
class CustomerUpdateView(DetailView):
    model = Customer
    template_name = 'tenant_customer/update/view.html'

    def get_object(self):
        customer = super().get_object()  # Call the superclass
        return customer                  # Return the object

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
        modified_context['current_page'] = "customers"

        # Return our modified context.
        return modified_context
