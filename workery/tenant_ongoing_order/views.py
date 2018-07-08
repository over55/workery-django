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
    ResourceItem,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder
)


class OngoingJobListView(LoginRequiredMixin, WorkeryListView):
    context_object_name = 'job_list'
    queryset = OngoingWorkOrder.objects.filter(
        state=ONGOING_WORK_ORDER_STATE.RUNNING
    ).order_by('-id').prefetch_related(
        'customer',
        'associate'
    )
    template_name = 'tenant_ongoing_order/summary/view.html'
    paginate_by = 100
    menu_id = 'ongoing-jobs'


class OngoingJobLiteRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/retrieve/lite_view.html'
    menu_id = 'ongoing-jobs'

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list',]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


class OngoingJobFullRetrieveView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/retrieve/full_view.html'
    menu_id = 'ongoing-jobs'

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list', 'task']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Get sorted values.
        job = modified_context['job']
        modified_context['ordered_closed_jobs'] = job.closed_orders.order_by('-id')

        # Return our modified context.
        return modified_context


class OngoingJobUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'job'
    model = OngoingWorkOrder
    template_name = 'tenant_ongoing_order/update/view.html'
    menu_id = 'ongoing-jobs'

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
