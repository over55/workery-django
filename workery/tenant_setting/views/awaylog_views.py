# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    AwayLog,
    SkillSet
)


class AwayLogListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'away_log_list'
    template_name = 'tenant_setting/awaylog/list_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = "settings" # Required for navigation

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our new context.
        return modified_context

    def get_queryset(self):
        queryset = AwayLog.objects.filter(
            was_deleted=False
        ).order_by(
            '-id'
        ).prefetch_related(
            'associate'
        )

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


class AwayLogUpdateView(LoginRequiredMixin, DetailView):
    context_object_name = 'away_log'
    model = AwayLog
    template_name = 'tenant_setting/awaylog/update_view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['menu_id'] = "settings"

        # Return our modified context.
        return modified_context


class AwayLogCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_setting/awaylog/create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "setting" # Required for navigation
        return context
