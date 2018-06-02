# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import WorkOrderFilter
from tenant_foundation.models import WorkOrder


class JobSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_order/search/search_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


class JobSearchResultView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    template_name = 'tenant_order/search/result_view.html'
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
            queryset = WorkOrder.objects.full_text_search(keyword)
        else:
            queryset = WorkOrder.objects.all()
            filter = WorkOrderFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        queryset = queryset.filter(is_archived=False)

        # Added join
        queryset = queryset.prefetch_related(
            'customer',
            'associate',
        )

        # Return our filtered results ordered by the specific order.
        return queryset.order_by('-assignment_date', '-completion_date', '-invoice_service_fee_payment_date')
