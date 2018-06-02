# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import Associate


#---------#
# SUMMARY #
#---------#


class MemberSummaryView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'associate_list'
    template_name = 'tenant_associate/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['menu_id'] = "associates"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context

    def get_queryset(self):
        queryset = Associate.objects.filter(
            owner__is_active=True
        ).prefetch_related(
            'owner'
        ).order_by('-id')
        return queryset


#------#
# LIST #
#------#


class MemberListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'associate_list'
    template_name = 'tenant_associate/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_id'] = "associates" # Required for navigation
        return context

    def get_queryset(self):
        queryset = Associate.objects.order_by(
            'given_name',
            'last_name'
        ).prefetch_related('owner')
        return queryset
