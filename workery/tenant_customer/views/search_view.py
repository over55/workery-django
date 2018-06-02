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
from tenant_foundation.models import Customer


class CustomerSearchView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_customer/search/search_view.html'
    menu_id = "customers"


class CustomerSearchResultView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_customer/search/result_view.html'
    paginate_by = 100
    menu_id = "customers"

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
            queryset = super(CustomerSearchResultView, self).get_queryset()
            filter = CustomerFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related('owner')

        return queryset
