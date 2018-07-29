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
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    Customer
)


class BlacklistedCustomerListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'customer_log_list'
    template_name = 'tenant_setting/blacklisted/list_view.html'
    paginate_by = 100
    menu_id = "settings"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = Customer.objects.filter(
            is_blacklisted=True
        ).order_by(
            '-id'
        ).prefetch_related(
            'owner'
        )

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset
