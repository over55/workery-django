# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import Associate


#--------#
# CREATE #
#--------#

@method_decorator(login_required, name='dispatch')
class MemberCreateView(TemplateView):
    template_name = 'tenant_associate/create/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates" # Required for navigation
        return context


#---------#
# SUMMARY #
#---------#


@method_decorator(login_required, name='dispatch')
class MemberSummaryView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'associate_list'
    queryset = Associate.objects.order_by('-created')
    template_name = 'tenant_associate/summary/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates" # Required for navigation
        return context

    def get_queryset(self):
        queryset = Associate.objects.all()
        queryset = queryset.order_by('-created')
        return queryset


#------#
# LIST #
#------#


@method_decorator(login_required, name='dispatch')
class MemberListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'associate_list'
    queryset = Associate.objects.order_by('-created')
    template_name = 'tenant_associate/list/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates" # Required for navigation
        return context

    def get_queryset(self):
        queryset = super(MemberListView, self).get_queryset() # Get the base.

        # The following code will use the 'django-filter'
        filter = AssociateFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


#--------#
# SEARCH #
#--------#


@method_decorator(login_required, name='dispatch')
class MemberSearchView(TemplateView):
    template_name = 'tenant_associate/search/search_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates"
        return context


@method_decorator(login_required, name='dispatch')
class MemberSearchResultView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'associate_list'
    queryset = Associate.objects.order_by('-created')
    template_name = 'tenant_associate/search/result_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "associates"

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
            queryset = Associate.objects.full_text_search(keyword)
            queryset = queryset.order_by('-created')
        else:
            queryset = super(MemberListView, self).get_queryset()

        # The following code will use the 'django-filter'
        filter = AssociateFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset


#----------#
# RETRIEVE #
#----------#


@method_decorator(login_required, name='dispatch')
class MemberRetrieveView(DetailView):
    model = Associate
    template_name = 'tenant_associate/retrieve/view.html'

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

        # Return our modified context.
        return modified_context


#----------#
# UPDATE #
#----------#


@method_decorator(login_required, name='dispatch')
class MemberUpdateView(DetailView):
    model = Associate
    template_name = 'tenant_associate/update/view.html'

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

        # Return our modified context.
        return modified_context
