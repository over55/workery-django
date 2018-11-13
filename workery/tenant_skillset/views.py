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
from tenant_foundation.models import (
    Associate,
    SkillSet
)


class SkillSetSearchView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'skill_set_list'
    template_name = 'tenant_skillset/search_view.html'
    paginate_by = 100
    menu_id = "skillsets"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = SkillSet.objects.all().order_by('sub_category')

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = "skillsets"
        modified_context['skillsets'] = SkillSet.objects.all().order_by('sub_category')
        return modified_context



class SkillSetSearchResultsView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'associate_list'
    template_name = 'tenant_skillset/result_view.html'
    paginate_by = 100
    menu_id = "skillsets"
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
        pks_string = self.request.GET.get('pks', None)
        pks_arr = pks_string.split(",")
        if pks_arr:
            queryset = Associate.objects.filter(skill_sets__in=pks_arr)
            queryset = queryset.order_by('last_name', 'given_name')

        # Attach skillsets.
        queryset = queryset.prefetch_related('skill_sets')

        return queryset

    def get_context_data(self, **kwargs):
        pks_string = self.request.GET.get('pks', None)
        pks_arr = pks_string.split(",")
        modified_context = super().get_context_data(**kwargs)

        arr = []
        for pk in pks_arr:
            arr.append(int(pk))
        modified_context['menu_id'] = "skillsets"
        modified_context['pks_arr'] = arr
        return modified_context
