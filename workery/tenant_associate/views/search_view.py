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
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import Associate


class MemberSearchView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_associate/search/search_view.html'
    menu_id = "associates"


class MemberSearchResultView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'associate_list'
    template_name = 'tenant_associate/search/result_view.html'
    paginate_by = 100
    menu_id = "associates"
    skip_parameters_array = ['page']

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = Associate.objects.full_text_search(keyword)
            queryset = queryset.order_by('last_name', 'given_name')
        else:
            queryset = Associate.objects.all()

            # The following code will use the 'django-filter'
            queryset = queryset.order_by('last_name', 'given_name')
            filter = AssociateFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related('owner')

        return queryset
