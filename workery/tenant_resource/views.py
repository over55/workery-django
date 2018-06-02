# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_foundation.models import ResourceCategory


class ResourceCategoryListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'resource_category_list'
    queryset = ResourceCategory.objects.all().order_by('id')
    template_name = 'tenant_resource/category_list_view.html'
    paginate_by = 100
    menu_id = "resource"


class ResourceCategoryRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'resource_category'
    model = ResourceCategory
    template_name = 'tenant_resource/category_retrieve.html'
    menu_id = "resource"
