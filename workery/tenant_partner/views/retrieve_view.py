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
from tenant_api.filters.partner import PartnerFilter
from tenant_foundation.models import Partner


class PartnerLiteRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'partner'
    model = Partner
    template_name = 'tenant_partner/retrieve/lite_view.html'
    menu_id = "partners"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class PartnerFullRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'partner'
    model = Partner
    template_name = 'tenant_partner/retrieve/full_view.html'
    menu_id = "partners"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_object(self):
        partner = super().get_object()  # Call the superclass
        return partner                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class PartnerCommentsRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'partner'
    model = Partner
    template_name = 'tenant_partner/retrieve/for/comments_view.html'
    menu_id = "partners"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_object(self):
        partner = super().get_object()  # Call the superclass
        return partner                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
    
    
class PartnerFilesRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'partner'
    model = Partner
    template_name = 'tenant_partner/retrieve/for/files_view.html'
    menu_id = "partners"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_object(self):
        partner = super().get_object()  # Call the superclass
        return partner                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
