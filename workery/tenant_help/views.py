# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    Staff,
    SkillSet,
    Tag,
    ResourceCategory,
    ResourceItem
)


class HelpCategoryListView(LoginRequiredMixin, ListView, ExtraRequestProcessingMixin):
    context_object_name = 'resource_category_list'
    queryset = ResourceCategory.objects.all().order_by('id')
    template_name = 'tenant_help/view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "resource"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class HelpCategoryRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'resource_category'
    model = ResourceCategory
    template_name = 'tenant_help/category_retrieve.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "resource"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


class HelpItemRetrieveView(LoginRequiredMixin, DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'resource_item'
    model = ResourceItem
    template_name = 'tenant_help/item_retrieve.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def query_pk_and_slug(self, pk, slug):
        return "3"

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "resource"

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context
