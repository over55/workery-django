# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_customer/customer_list.html'
    paginate_by = 100

    # def head(self, *args, **kwargs):
    #     last_customer = self.get_queryset().latest('-last_modified')
    #     response = HttpResponse('')
    #     # RFC 1123 date format
    #     response['Last-Modified'] = last_customer.last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
    #     return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers"
        return context

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None  # The queryset we will be returning.

        # Either apply search or narrow down the searches.
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


@method_decorator(login_required, name='dispatch')
class CustomerSearchView(TemplateView):
    template_name = 'tenant_customer/customer_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers"
        return context


@method_decorator(login_required, name='dispatch')
class CustomerCreateView(TemplateView):
    template_name = 'tenant_customer/customer_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers"
        return context


@method_decorator(login_required, name='dispatch')
class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'tenant_customer/customer_detail.html'

    def get_object(self):
        customer = super().get_object()  # Call the superclass
        return customer  # Return the object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "customers"
        return context
