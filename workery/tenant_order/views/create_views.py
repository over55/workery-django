# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import Customer, Order, OrderServiceFee, SkillSet, Tag


class Step1ACreateOrAddCustomerView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/create/step_1_a_search_or_add_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs" # Required for navigation
        return context


class Step1BCustomerSearchResultsView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'customer_list'
    queryset = Customer.objects.order_by('-created')
    template_name = 'tenant_order/create/step_1_b_search_results_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "jobs"

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
            queryset = super(Step1BCustomerSearchResultsView, self).get_queryset()
            filter = CustomerFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        return queryset


class Step2View(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/create/step_2_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


class Step3View(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/create/step_3_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


class Step4View(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/create/step_4_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = "jobs"
        modified_context['skillsets'] = SkillSet.objects.all()
        modified_context['servicefees'] = OrderServiceFee.objects.all()
        return modified_context


class Step5View(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/create/step_5_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


class Step6View(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/create/step_6_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context
