# -*- coding: utf-8 -*-


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
