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
from tenant_api.filters.partner import PartnerFilter
from tenant_foundation.models import Partner


class PartnerSearchView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_partner/search/search_view.html'
    menu_id = "partners"


class PartnerSearchResultView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'partner_list'
    template_name = 'tenant_partner/search/result_view.html'
    paginate_by = 100
    menu_id = "partners"
    skip_parameters_array = ['page']

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = Partner.objects.full_text_search(keyword)
            queryset = queryset.order_by('last_name', 'given_name')
        else:
            queryset = Partner.objects.all()

            # The following code will use the 'django-filter'
            queryset = queryset.order_by('last_name', 'given_name')
            filter = PartnerFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related('owner')

        return queryset
