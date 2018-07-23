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
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import Associate


class MemberSearchView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_associate/search/search_view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class MemberSearchResultView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'associate_list'
    template_name = 'tenant_associate/search/result_view.html'
    paginate_by = 100
    menu_id = "associates"
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
            queryset = Associate.objects.full_text_search(keyword)
            queryset = queryset.order_by('last_name', 'given_name')
        else:
            # Remove special characters from the telephone
            tel = self.request.GET.get('telephone')
            tel = tel.replace('(', '')
            tel = tel.replace(')', '')
            tel = tel.replace('-', '')
            tel = tel.replace('+', '')
            tel = tel.replace(' ', '')
            self.request.GET._mutable = True
            self.request.GET['telephone'] = tel

            # Order our data.
            queryset = Associate.objects.all()
            queryset = queryset.order_by('last_name', 'given_name')

            # The following code will use the 'django-filter'
            filter = AssociateFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related('owner')

        return queryset
