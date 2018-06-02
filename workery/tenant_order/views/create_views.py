# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView
)
from tenant_api.filters.order import WorkOrderFilter
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer, WorkOrder, WorkOrderServiceFee, SkillSet, Tag


class Step1ACreateOrAddCustomerView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/create/step_1_a_search_or_add_view.html'
    menu_id = 'jobs'


class Step1BCustomerSearchResultsView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_order/create/step_1_b_search_results_view.html'
    paginate_by = 100
    menu_id = 'jobs'
    skip_parameters_array = ['page']

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
            queryset = super(Step1BCustomerSearchResultsView, self).get_queryset()
            filter = CustomerFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        return queryset


class Step2View(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/create/step_2_view.html'
    menu_id = 'jobs'


class Step3View(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/create/step_3_view.html'
    menu_id = 'jobs'


class Step4View(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/create/step_4_view.html'
    menu_id = 'jobs'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = "jobs"
        modified_context['skillsets'] = SkillSet.objects.all()
        modified_context['servicefees'] = WorkOrderServiceFee.objects.all()
        return modified_context


class Step5View(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/create/step_5_view.html'
    menu_id = 'jobs'


class Step6View(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_order/create/step_6_view.html'
    menu_id = 'jobs'
