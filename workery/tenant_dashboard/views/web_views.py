# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    Order,
    TaskItem
)


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView, ExtraRequestProcessingMixin):
    """
    The default entry point into our dashboard.
    """

    template_name = 'tenant_dashboard/master_view.html'

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        modified_context['current_page'] = 'dashboard' # Required

        modified_context['associates_count'] = Associate.objects.filter(
            owner__is_active=True
        ).count()

        modified_context['customers_count'] = Customer.objects.all().count()

        modified_context['jobs_count'] = Order.objects.filter(
            is_cancelled=False,
            completion_date__isnull=True,
            invoice_service_fee_payment_date__isnull=True
        ).count()

        modified_context['tasks_count'] = TaskItem.objects.filter(
            is_closed=False
        ).count()

        modified_context['awaylogs'] = AwayLog.objects.filter(was_deleted=False)

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our
        #   `modified_context` so we can use in this view.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context
