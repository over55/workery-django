# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    Staff,
    SkillSet,
    Tag,
    ResourceCategory,
    ResourceItem
)


class HelpCategoryListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'resource_category_list'
    queryset = ResourceCategory.objects.all().order_by('id')
    template_name = 'tenant_help/view.html'
    paginate_by = 100
    menu_id = "resource"


class HelpCategoryRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'resource_category'
    model = ResourceCategory
    template_name = 'tenant_help/category_retrieve.html'
    menu_id = "resource"


class HelpItemRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'resource_item'
    model = ResourceItem
    template_name = 'tenant_help/item_retrieve.html'
    menu_id = "resource"

    def query_pk_and_slug(self, pk, slug):
        return "3"
