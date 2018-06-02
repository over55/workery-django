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
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import (
    AwayLog,
    SkillSet
)


class AwayLogListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'away_log_list'
    template_name = 'tenant_setting/awaylog/list_view.html'
    paginate_by = 100
    menu_id = "settings"

    def get_queryset(self):
        queryset = AwayLog.objects.filter(
            was_deleted=False
        ).order_by(
            '-id'
        ).prefetch_related(
            'associate'
        )

        # # The following code will use the 'django-filter'
        # filter = CustomerFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        return queryset


class AwayLogUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'away_log'
    model = AwayLog
    template_name = 'tenant_setting/awaylog/update_view.html'
    menu_id = "settings"


class AwayLogCreateView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_setting/awaylog/create_view.html'
    menu_id = "settings"
