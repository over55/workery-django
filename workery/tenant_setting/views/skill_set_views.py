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
    InsuranceRequirement,
    SkillSet,
    Tag
)


class SkillSetListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'skill_set_list'
    template_name = 'tenant_setting/skill_set/list_view.html'
    paginate_by = 100
    menu_id = "settings"

    def get_queryset(self):
        queryset = SkillSet.objects.all().order_by('category', 'sub_category')

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


class SkillSetUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'skill_set'
    model = SkillSet
    template_name = 'tenant_setting/skill_set/update_view.html'
    menu_id = "settings"

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Add extra database lookups.
        modified_context['insurance_requirements'] = InsuranceRequirement.objects.all()

        # Return our modified context.
        return modified_context


class SkillSetCreateView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_setting/skill_set/create_view.html'
    menu_id = "settings"

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Add extra database lookups.
        modified_context['insurance_requirements'] = InsuranceRequirement.objects.all()

        # Return our modified context.
        return modified_context
