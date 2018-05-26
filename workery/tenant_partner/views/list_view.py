# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.partner import PartnerFilter
from tenant_foundation.models import Partner


#---------#
# SUMMARY #
#---------#


class PartnerSummaryView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'partner_list'
    template_name = 'tenant_partner/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "partners"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context

    def get_queryset(self):
        queryset = Partner.objects.filter(owner__is_active=True).order_by('-id').prefetch_related(
            'owner',
        )
        return queryset


#------#
# LIST #
#------#


class PartnerListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'partner_list'
    template_name = 'tenant_partner/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "partners" # Required for navigation
        return context

    def get_queryset(self):
        queryset = Partner.objects.order_by('given_name', 'last_name').prefetch_related(
            'owner',
        )
        return queryset
