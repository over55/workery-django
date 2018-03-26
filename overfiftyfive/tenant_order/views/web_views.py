# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_foundation.models.order import Order


#--------#
# CREATE #
#--------#

@method_decorator(login_required, name='dispatch')
class JobCreateView(TemplateView):
    template_name = 'tenant_order/create/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs" # Required for navigation
        return context


#---------#
# SUMMARY #
#---------#


@method_decorator(login_required, name='dispatch')
class JobSummaryView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.order_by('-created')
    template_name = 'tenant_order/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context

    def get_queryset(self):
        queryset = Order.objects.all()
        queryset = queryset.order_by('-assignment_date', '-completion_date', '-payment_date') # Get the base.
        return queryset


#------#
# LIST #
#------#


@method_decorator(login_required, name='dispatch')
class JobListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.order_by('-created')
    template_name = 'tenant_order/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs" # Required for navigation
        return context

    def get_queryset(self):
        queryset = super(JobListView, self).get_queryset().order_by('-assignment_date', '-completion_date', '-payment_date') # Get the base.

        # The following code will use the 'django-filter'
        filter = OrderFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


#--------#
# SEARCH #
#--------#


@method_decorator(login_required, name='dispatch')
class JobSearchView(TemplateView):
    template_name = 'tenant_order/search/search_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "jobs"
        return context


@method_decorator(login_required, name='dispatch')
class JobSearchResultView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    template_name = 'tenant_order/search/result_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # DEVELOPERS NOTE:
        # - This class based view will have URL parameters for filtering and
        #   searching records.
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['filter_parameters'] = self.get_param_urls(['page'])

        # Return our modified context.
        return modified_context

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None  # The queryset we will be returning.
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = Order.objects.full_text_search(keyword)
        else:
            queryset = Order.objects.all()
            filter = OrderFilter(self.request.GET, queryset=queryset)
            queryset = filter.qs

        # Return our filtered results ordered by the specific order.
        return queryset.order_by('-assignment_date', '-completion_date', '-payment_date')


#----------#
# RETRIEVE #
#----------#


@method_decorator(login_required, name='dispatch')
class JobRetrieveView(DetailView):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/retrieve/view.html'

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

        # Return our modified context.
        return modified_context


#--------#
# UPDATE #
#--------#


@method_decorator(login_required, name='dispatch')
class JobUpdateView(DetailView):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/update/view.html'

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

        # Return our modified context.
        return modified_context
