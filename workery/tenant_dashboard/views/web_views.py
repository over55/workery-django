# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    WORK_ORDER_STATE,
    WorkOrder,
    TaskItem
)


class DashboardView(LoginRequiredMixin, WorkeryTemplateView):
    """
    The default entry point into our dashboard.
    """
    template_name = 'tenant_dashboard/master_view.html'
    menu_id = "dashboard"

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        modified_context['associates_count'] = Associate.objects.filter(
            owner__is_active=True
        ).count()

        modified_context['customers_count'] = Customer.objects.all().count()

        modified_context['jobs_count'] = WorkOrder.objects.filter(
            ~Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID) &
            ~Q(state=WORK_ORDER_STATE.ARCHIVED) &
            ~Q(state=WORK_ORDER_STATE.CANCELLED)
        ).count()

        modified_context['tasks_count'] = TaskItem.objects.filter(
            is_closed=False
        ).count()

        modified_context['awaylogs'] = AwayLog.objects.filter(
            was_deleted=False
        ).prefetch_related(
            'associate'
        )

        # Return our modified context.
        return modified_context
