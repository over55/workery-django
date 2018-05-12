# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    SkillSet,
    Tag
)


@method_decorator(login_required, name='dispatch')
class SkillSetListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'skill_set_list'
    template_name = 'tenant_setting/skill_set/list_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['current_page'] = "settings" # Required for navigation

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our new context.
        return modified_context

    def get_queryset(self):
        queryset = SkillSet.objects.all().order_by('category', 'sub_category', 'insurance_requirement')

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


@method_decorator(login_required, name='dispatch')
class SkillSetUpdateView(DetailView):
    context_object_name = 'skill_set'
    model = SkillSet
    template_name = 'tenant_setting/skill_set/update_view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "settings"

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class SkillSetCreateView(TemplateView):
    template_name = 'tenant_setting/skill_set/create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "setting" # Required for navigation
        return context
