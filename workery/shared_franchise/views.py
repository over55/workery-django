# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from shared_foundation.models import SharedFranchise


#TODO: UNIT TEST


@method_decorator(login_required, name='dispatch')
class FranchiseListView(ListView):
    context_object_name = 'franchise_list'
    template_name = 'shared_franchise/list_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = "franchise"
        return modified_context

    def get_queryset(self):
        queryset = SharedFranchise.objects.filter(~Q(schema_name="public")).order_by('-id')
        return queryset


@method_decorator(login_required, name='dispatch')
class FranchiseCreatePage1of3View(TemplateView):
    template_name = 'shared_franchise/create_1_of_3_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = 'franchise' # Required
        modified_context['timezones'] = pytz.common_timezones
        return modified_context # Return our modified context.


@method_decorator(login_required, name='dispatch')
class FranchiseCreatePage2of3View(TemplateView):
    template_name = 'shared_franchise/create_2_of_3_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = 'franchise' # Required
        return modified_context # Return our modified context.


@method_decorator(login_required, name='dispatch')
class FranchiseCreatePage3of3View(TemplateView):
    template_name = 'shared_franchise/create_3_of_3_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)
        modified_context['menu_id'] = 'franchise' # Required
        return modified_context # Return our modified context.
