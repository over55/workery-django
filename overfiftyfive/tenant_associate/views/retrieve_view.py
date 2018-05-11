# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import ActivitySheetItem, Associate


@method_decorator(login_required, name='dispatch')
class MemberLiteRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/lite_view.html'

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

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
        modified_context['current_page'] = "associates"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        associate = modified_context['associate']
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(associate=associate)

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class MemberFullRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/full_view.html'

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

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
        modified_context['current_page'] = "associates"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        associate = modified_context['associate']
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(associate=associate)

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class MemberRetrieveForCommentsListAndCreateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/for/comments_view.html'

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

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
        modified_context['current_page'] = "associates"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class MemberRetrieveForActivitySheetListView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/for/activity_sheet_view.html'

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

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
        modified_context['current_page'] = "associates"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # #
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(
            associate = modified_context['associate']
        ).order_by("-created_at")

        # Return our modified context.
        return modified_context
