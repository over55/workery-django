# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    SkillSet,
    Tag
)


@method_decorator(login_required, name='dispatch')
class TagListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'tag_list'
    template_name = 'tenant_setting/tag/list_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "settings" # Required for navigation
        return context

    def get_queryset(self):
        queryset = Tag.objects.all().order_by('id')

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset




@method_decorator(login_required, name='dispatch')
class TagUpdateView(DetailView):
    context_object_name = 'tag'
    model = Tag
    template_name = 'tenant_setting/tag/update_view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "settings"

        # Return our modified context.
        return modified_context
