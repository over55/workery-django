# -*- coding: utf-8 -*-
from django.views.generic import DetailView, ListView, TemplateView


class ExtraRequestProcessingMixin(object):
    """
    Mixin used to get extract the filter parameters from the request GET
    variables.
    """
    def get_param_urls(self, skip_parameters_array):
        parameters = ""
        for param in self.request.GET:
            if str(param) not in skip_parameters_array:
                parameter = "&"+param+"="+self.request.GET.get(param, None)
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
        base_context['url_parameters'] = self.get_param_urls(self.skip_parameters_array)

        # Return our custom context based on our `workery` app.
        return base_context


class WorkeryListView(ListView, ExtraRequestProcessingMixin):
    """
    An opinionated modification on the class-based "ListView" view to
    have a few enhancements suited for our `workery` app.
    """
    menu_id =  None  # Required for navigation
    workery_skip_parameters_array = []

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
        base_context['url_parameters'] = self.get_param_urls(self.workery_skip_parameters_array)

        # Return our custom context based on our `workery` app.
        return base_context
