# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from tenant_foundation.models import Customer


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_customer/customer_list.html'
    paginate_by = 100


@method_decorator(login_required, name='dispatch')
class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'tenant_customer/customer_detail.html'

    def get_object(self):
        customer = super().get_object()  # Call the superclass
        return customer  # Return the object
