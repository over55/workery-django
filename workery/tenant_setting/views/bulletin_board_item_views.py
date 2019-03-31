# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    GroupRequiredMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    BulletinBoardItem,
    SkillSet
)


class BulletinBoardItemListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryListView):
    context_object_name = 'away_log_list'
    template_name = 'tenant_setting/bulletin_board_item/list_view.html'
    paginate_by = 100
    menu_id = "settings"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_queryset(self):
        queryset = BulletinBoardItem.objects.filter(
            is_archived=False
        ).order_by(
            '-id'
        ).prefetch_related(
            'created_by',
            'last_modified_by'
        )

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


class BulletinBoardItemUpdateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'away_log'
    model = BulletinBoardItem
    template_name = 'tenant_setting/bulletin_board_item/update_view.html'
    menu_id = "settings"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]


class BulletinBoardItemCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_setting/bulletin_board_item/create_view.html'
    menu_id = "settings"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]
