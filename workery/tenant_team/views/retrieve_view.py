# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import Staff


class StaffLiteRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'staff'
    model = Staff
    template_name = 'tenant_team/retrieve/lite_view.html'

    def get_object(self):
        staff = super().get_object()  # Call the superclass
        return staff                  # Return the object

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
        modified_context['menu_id'] = "team"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class StaffFullRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'staff'
    model = Staff
    template_name = 'tenant_team/retrieve/full_view.html'

    def get_object(self):
        staff = super().get_object()  # Call the superclass
        return staff                  # Return the object

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
        modified_context['menu_id'] = "team"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class StaffRetrieveForCommentsListAndCreateView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'staff'
    model = Staff
    template_name = 'tenant_team/retrieve/for/comments_view.html'

    def get_object(self):
        staff = super().get_object()  # Call the superclass
        return staff                  # Return the object

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
        modified_context['menu_id'] = "team"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


def staff_redirect_from_user_id_to_staff_id(request, template, pk):
    from django.urls import reverse
    staff = Staff.objects.filter(owner__id=pk).first()
    if staff:
        return HttpResponseRedirect(reverse('workery_tenant_team_retrieve', args=[template, pk]))
    else:
        return HttpResponseBadRequest(_('Cannot find user id.'))
