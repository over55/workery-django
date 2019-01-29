# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView


 #TODO: UNIT TEST


class GroupRequiredMixin(object):
    """
    Mixin used to restrict authenticated user access to the required group
    specified in the class-based view.
    """
    group_required = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(id__in=self.group_required):
                return super(GroupRequiredMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied(_('You do not belong to group which was granted access to this view.'))


class ExtraRequestProcessingMixin(object):
    """
    Mixin used to get extract the filter parameters from the request GET
    variables.
    """
    def get_param_urls(self, skip_parameters_array):
        parameters = ""
        for i, param in  enumerate(self.request.GET):
            if str(param) not in skip_parameters_array:

                # Figure out whether to use '?' or '&' operation.
                operation = '?'
                if i > 0:
                    operation = '&'

                # Generate the URL.
                parameter = operation + param + "=" + self.request.GET.get(param, None)
                parameters += parameter

        return parameters


    def get_params_dict(self, skip_parameters_array):
        parameters = {}
        for param in self.request.GET:
            if str(param) not in skip_parameters_array:
                parameters[param] = self.request.GET.get(param, None)
        return parameters


class WorkeryTemplateView(TemplateView, ExtraRequestProcessingMixin):
    """
    An opinionated modification on the class-based "TemplateView" view to
    have a few enhancements suited for our `workery` app.
    """
    menu_id =  None  # Required for navigation
    skip_parameters_array = []

    def get_context_data(self, **kwargs):
        """
        Override the 'get_context_data' function do add our enhancements.
        """
        base_context = super().get_context_data(**kwargs)

        # Attach a "menu_id" object to the view.
        base_context['menu_id'] = self.menu_id

        # DEVELOPERS NOTE:
        # - This class based view will have URL parameters for filtering and
        #   searching records.
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        base_context['filter_parameters'] = self.get_param_urls(self.skip_parameters_array)
        base_context['parameters'] = self.get_params_dict(self.skip_parameters_array)

        # Return our custom context based on our `workery` app.
        return base_context


class WorkeryListView(ListView, ExtraRequestProcessingMixin):
    """
    An opinionated modification on the class-based "ListView" view to
    have a few enhancements suited for our `workery` app.
    """
    menu_id =  None  # Required for navigation
    skip_parameters_array = []

    def get_context_data(self, **kwargs):
        """
        Override the 'get_context_data' function do add our enhancements.
        """
        base_context = super().get_context_data(**kwargs)

        # Attach a "menu_id" object to the view.
        base_context['menu_id'] = self.menu_id

        # DEVELOPERS NOTE:
        # - This class based view will have URL parameters for filtering and
        #   searching records.
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        base_context['filter_parameters'] = self.get_param_urls(self.skip_parameters_array)
        base_context['parameters'] = self.get_params_dict(self.skip_parameters_array)

        # Return our custom context based on our `workery` app.
        return base_context

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)


class WorkeryDetailView(DetailView, ExtraRequestProcessingMixin):
    """
    An opinionated modification on the class-based "ListView" view to
    have a few enhancements suited for our `workery` app.
    """
    menu_id =  None  # Required for navigation
    skip_parameters_array = []

    def get_context_data(self, **kwargs):
        """
        Override the 'get_context_data' function do add our enhancements.
        """
        base_context = super().get_context_data(**kwargs)

        # Attach a "menu_id" object to the view.
        base_context['menu_id'] = self.menu_id

        # DEVELOPERS NOTE:
        # - This class based view will have URL parameters for filtering and
        #   searching records.
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        base_context['filter_parameters'] = self.get_param_urls(self.skip_parameters_array)
        base_context['parameters'] = self.get_params_dict(self.skip_parameters_array)

        # Return our custom context based on our `workery` app.
        return base_context


class ReturnIDParameterRequiredMixin(object):
    """
    Mixin used to restrict access to view based on whether the parameter in the
    URL matches the specified IDs.

    REQUIRED:
    - return_id

    OPTIONAL:
    - return_task_id
    """
    return_id_required = []

    def dispatch(self, request, *args, **kwargs):
        return_id = request.GET.get('return_id', None)
        if return_id not in self.return_id_required:
            raise PermissionDenied(_('You entered wrong format.'))
        return super(ReturnIDParameterRequiredMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Override the 'get_context_data' function do add our enhancements.
        """
        base_context = super().get_context_data(**kwargs)

        # Attach the URL parameter to our view.
        base_context['return_id'] = self.request.GET.get('return_id', None) # REQUIRED
        base_context['return_task_id'] = self.request.GET.get('return_task_id', None) # OPTIONAL

        # Return our custom context based on our `workery` app.
        return base_context


class ParentNodeURLParameterRequiredMixin(object):
    parent_node_required = []

    def dispatch(self, request, *args, **kwargs):

        # Validate the template selected.
        parent_node = self.kwargs['parent_node']
        if parent_node not in self.parent_node_required:
            raise PermissionDenied(_('You entered wrong format.'))

        return super(ParentNodeURLParameterRequiredMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Override the 'get_context_data' function do add our enhancements.
        """
        base_context = super().get_context_data(**kwargs)

        # Attach the URL parameter to our view.
        base_context['parent_node'] = self.request.GET.get('parent_node', None)

        # Return our custom context based on our `workery` app.
        return base_context
