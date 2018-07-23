# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
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
from tenant_api.filters.order import WorkOrderFilter
from tenant_foundation.models import WorkOrder, WORK_ORDER_STATE


class JobSearchView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/search/search_view.html'
    menu_id = 'jobs'
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class JobSearchResultView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    template_name = 'tenant_order/search/result_view.html'
    paginate_by = 100
    menu_id = 'jobs'
    skip_parameters_array = ['page']
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = WorkOrder.objects.full_text_search(keyword)
        else:
            queryset = WorkOrder.objects.all()
            filter = WorkOrderFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        queryset = queryset.exclude(state=WORK_ORDER_STATE.ARCHIVED)

        # Added join
        queryset = queryset.prefetch_related(
            'customer',
            'associate',
        )

        # Return our filtered results ordered by the specific order.
        return queryset.order_by('-assignment_date', '-completion_date', '-invoice_service_fee_payment_date')
