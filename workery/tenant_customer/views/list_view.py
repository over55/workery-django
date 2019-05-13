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
from tenant_foundation.models import Customer


class CustomerSummaryView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'customer_list'
    template_name = 'tenant_customer/summary/view.html'
    paginate_by = 100
    menu_id = 'customers'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Customer.objects.filter(
            state=Customer.CUSTOMER_STATE.ACTIVE
        ).prefetch_related(
            'owner'
        ).order_by(
            'last_name',
            'given_name',
        )

        # The following code will use the 'django-filter'.
        filter = CustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


class CustomerListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'customer_list'
    template_name = 'tenant_customer/list/view.html'
    paginate_by = 100
    menu_id = 'customers'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Customer.objects.all().prefetch_related(
            'owner'
        ).order_by(
            'last_name',
            'given_name',
        )

        # The following code will use the 'django-filter'.
        filter = CustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset
