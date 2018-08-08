# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    GroupRequiredMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Comment,
    Customer,
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    TaskItem
)


def get_todays_date_minus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() - timedelta(days=days)


class DashboardView(LoginRequiredMixin, GroupRequiredMixin, WorkeryTemplateView):
    """
    The default entry point into our dashboard.
    """
    template_name = 'tenant_dashboard/master_view.html'
    menu_id = "dashboard"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        modified_context['associates_count'] = Associate.objects.filter(
            owner__is_active=True
        ).count()

        modified_context['customers_count'] = Customer.objects.all().count()

        modified_context['jobs_count'] = WorkOrder.objects.filter(
            Q(state=WORK_ORDER_STATE.NEW) |
            Q(state=WORK_ORDER_STATE.PENDING) |
            Q(state=WORK_ORDER_STATE.ONGOING) |
            Q(state=WORK_ORDER_STATE.IN_PROGRESS)
        ).count()

        modified_context['tasks_count'] = TaskItem.objects.filter(
            is_closed=False
        ).count()

        modified_context['awaylogs'] = AwayLog.objects.filter(
            was_deleted=False
        ).prefetch_related(
            'associate'
        )

        one_week_before_today = get_todays_date_minus_days(5)
        modified_context['past_few_day_comments'] = WorkOrderComment.objects.filter(
            created_at__gte=one_week_before_today
        ).order_by(
            '-created_at'
        ).prefetch_related(
            'about',
            'comment'
        )

        # Return our modified context.
        return modified_context
