# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_foundation.models import Associate, Customer, Order, SkillSet


@method_decorator(login_required, name='dispatch')
class JobRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/order_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class JobCommentsRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/comments_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context




@method_decorator(login_required, name='dispatch')
class JobActivitySheetRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/activity_sheet_view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Find all the associates that match the job skill criteria.
        job = modified_context['job']
        skill_set_pks = job.skill_sets.values_list('pk', flat=True)
        print(skill_set_pks)
        available_associates = Associate.objects.filter(skill_sets__in=skill_set_pks)
        print(available_associates)

        # Return our modified context.
        return modified_context
