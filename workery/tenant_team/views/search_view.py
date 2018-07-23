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
from tenant_foundation.models import Staff


#--------#
# SEARCH #
#--------#


class TeamSearchView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_team/search/search_view.html'
    menu_id = "team"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class TeamSearchResultView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'staff_list'
    template_name = 'tenant_team/search/result_view.html'
    paginate_by = 100
    menu_id = "team"
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
            queryset = Staff.objects.full_text_search(keyword)
            queryset = queryset.order_by('last_name', 'given_name')
        else:
            queryset = Staff.objects.all()
            queryset = queryset.order_by('last_name', 'given_name')

            # Remove special characters from the telephone
            tel = self.request.GET.get('telephone')
            tel = tel.replace('(', '')
            tel = tel.replace(')', '')
            tel = tel.replace('-', '')
            tel = tel.replace('+', '')
            tel = tel.replace(' ', '')
            self.request.GET._mutable = True
            self.request.GET['telephone'] = tel

            # The following code will use the 'django-filter' library.
            filter = StaffFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Attach owners.
        queryset = queryset.prefetch_related('owner')

        return queryset
