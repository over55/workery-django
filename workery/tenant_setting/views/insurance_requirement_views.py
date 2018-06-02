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
from tenant_foundation.models import InsuranceRequirement


class TagListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'insurance_requirement_list'
    template_name = 'tenant_setting/insurance_requirement/list_view.html'
    paginate_by = 100
    menu_id = "settings"

    def get_queryset(self):
        queryset = InsuranceRequirement.objects.all().order_by('text')

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


class TagUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'insurance_requirement'
    model = InsuranceRequirement
    template_name = 'tenant_setting/insurance_requirement/update_view.html'
    menu_id = "settings"


class TagCreateView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_setting/insurance_requirement/create_view.html'
    menu_id = "settings"
