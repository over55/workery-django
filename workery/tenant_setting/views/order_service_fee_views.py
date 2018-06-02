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
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    SkillSet,
    WorkOrderServiceFee
)


class WorkOrderServiceFeeListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'order_service_fee_list'
    template_name = 'tenant_setting/order_service_fee/list_view.html'
    paginate_by = 100
    menu_id = "settings"

    def get_queryset(self):
        queryset = WorkOrderServiceFee.objects.all().order_by('title')

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


class WorkOrderServiceFeeUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'order_service_fee'
    model = WorkOrderServiceFee
    template_name = 'tenant_setting/order_service_fee/update_view.html'
    menu_id = "settings"


class WorkOrderServiceFeeCreateView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_setting/order_service_fee/create_view.html'
    menu_id = "settings"
