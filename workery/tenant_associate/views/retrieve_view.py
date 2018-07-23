# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
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
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import ActivitySheetItem, Associate, WorkOrder


class MemberLiteRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/lite_view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        associate = modified_context['associate']
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(associate=associate)

        # Return our modified context.
        return modified_context


class MemberFullRetrieveView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/full_view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        associate = modified_context['associate']
        modified_context['activity_sheet_items'] = ActivitySheetItem.objects.filter(associate=associate)

        # Return our modified context.
        return modified_context


class MemberRetrieveForCommentsListAndCreateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/for/comments_view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

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


class MemberRetrieveForActivitySheetListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/for/activity_sheet_view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Lookup the acitivty sheet items for this associate.
        activity_sheet_items = ActivitySheetItem.objects.filter(
            associate = modified_context['associate']
        ).prefetch_related(
            'job',
            'associate',
        ).order_by("-id")

        paginator = Paginator(activity_sheet_items, 25) # Show 25 contacts per page
        page = self.request.GET.get('page', 1)
        paginated_activity_sheet_items = paginator.get_page(page)

        modified_context['paginated_activity_sheet_items'] = paginated_activity_sheet_items

        # Return our modified context.
        return modified_context


class MemberRetrieveForJobsListView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/retrieve/for/jobs_view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Lookup the acitivty sheet items for this associate.
        jobs = WorkOrder.objects.filter(
            associate = modified_context['associate']
        ).prefetch_related(
            'associate',
            'customer'
        ).order_by("-id")

        paginator = Paginator(jobs, 25) # Show 25 contacts per page
        page = self.request.GET.get('page', 1)
        jobs_items = paginator.get_page(page)

        modified_context['paginated_job_items'] = jobs_items

        # Return our modified context.
        return modified_context
