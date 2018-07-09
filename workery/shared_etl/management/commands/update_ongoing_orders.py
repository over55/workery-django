# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from dateutil import tz
from decimal import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from tenant_foundation.constants import *
from tenant_foundation.models import ACTIVITY_SHEET_ITEM_STATE
from tenant_foundation.models import ActivitySheetItem
from tenant_foundation.models.work_order import WORK_ORDER_STATE
from tenant_foundation.models.taskitem import TaskItem
from tenant_foundation.models.work_order import WorkOrder
from tenant_foundation.models.ongoing_work_order import ONGOING_WORK_ORDER_STATE
from tenant_foundation.models.ongoing_work_order import OngoingWorkOrder


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class Command(BaseCommand):
    """
    python manage.py update_ongoing_orders
    """
    help = _('ETL will iterate through all ongoing jobs in all tenants and create the specific work orders for this month.')

    def handle(self, *args, **options):
        franchises = SharedFranchise.objects.filter(
            ~Q(schema_name="public") &
            ~Q(schema_name="test")
        )
        for franchise in franchises.all():
            # Connection needs first to be at the public schema, as this is where
            # the database needs to be set before creating a new tenant. If this is
            # not done then django-tenants will raise a "Can't create tenant outside
            # the public schema." error.
            connection.set_schema_to_public() # Switch to Public.

            # Connection will set it back to our tenant.
            connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

            # Run the command which exists in the franchise.
            self.run_update_ongoing_jobs_for_franchise(franchise)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all ongoing job orders.'))
        )

    def run_update_ongoing_jobs_for_franchise(self, franchise):
        """
        Function will iterate through all the `running` ongoing work orders and
        perform the necessary operations.
        """
        ongoing_jobs = OngoingWorkOrder.objects.filter(state=ONGOING_WORK_ORDER_STATE.RUNNING, open_order=None)
        for ongoing_job in ongoing_jobs.all():
            self.open_new_work_order(ongoing_job)

    def open_new_work_order(self, ongoing_job):
        # Fetch our most recent closed job.
        previous_order = ongoing_job.closed_orders.order_by('-id').first()

        # Create a new job based on the previously closed job data
        new_order = WorkOrder.objects.create(
            customer = previous_order.customer,
            associate = previous_order.associate,
            description = previous_order.description,
            assignment_date = previous_order.assignment_date,
            # tags = previous_order.tags,
            is_ongoing = previous_order.is_ongoing,
            is_home_support_service = previous_order.is_home_support_service,
            start_date = previous_order.start_date,
            completion_date = previous_order.completion_date,
            hours = previous_order.hours,
            # skill_sets = previous_order.skill_sets,
            type_of = previous_order.type_of,
            indexed_text = previous_order.indexed_text,
            # comments = previous_order.comments,
            follow_up_days_number = previous_order.follow_up_days_number,
            closing_reason = previous_order.closing_reason,
            closing_reason_other = previous_order.closing_reason_other,
            latest_pending_task = None, # Create new one!
            # activity_sheet = previous_order.activity_sheet,
            state = previous_order.state,
            was_job_satisfactory = previous_order.was_job_satisfactory,
            was_job_finished_on_time_and_on_budget = previous_order.was_job_finished_on_time_and_on_budget,
            was_associate_punctual = previous_order.was_associate_punctual,
            was_associate_professional = previous_order.was_associate_professional,
            would_customer_refer_our_organization = previous_order.would_customer_refer_our_organization,
            score = previous_order.score,
            invoice_date = previous_order.invoice_date,
            invoice_id = previous_order.invoice_id,
            invoice_quote_amount = previous_order.invoice_quote_amount,
            invoice_labour_amount = previous_order.invoice_labour_amount,
            invoice_material_amount = previous_order.invoice_material_amount,
            invoice_tax_amount = previous_order.invoice_tax_amount,
            invoice_total_amount = previous_order.invoice_total_amount,
            invoice_service_fee_amount = previous_order.invoice_service_fee_amount,
            invoice_service_fee = previous_order.invoice_service_fee,
            invoice_service_fee_payment_date = previous_order.invoice_service_fee_payment_date,
            ongoing_work_order = ongoing_job,
        )

        # Update sets.
        new_order.tags.set(previous_order.tags.all())
        new_order.skill_sets.set(previous_order.skill_sets.all())
        # new_order.comments.set(previous_order.comments.all())
        # new_order.activity_sheet.set(previous_order.activity_sheet.all())

        # Create our activity sheet.
        if previous_order.associate:  # ... but only if an associate was assigned!
            new_activity_sheet = ActivitySheetItem.objects.create(
                job = new_order,
                associate = previous_order.associate,
                state = ACTIVITY_SHEET_ITEM_STATE.ACCEPTED
            )

        # Create our new task for following up.
        next_task_item = TaskItem.objects.create(
            type_of = FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
            title = _('Completion Survey'),
            description = _('Please call up the client and perform the satisfaction survey.'),
            due_date = get_todays_date_plus_days(7),
            is_closed = False,
            job = new_order
        )

        # Attach our follow up task to the newly created task.
        new_order.latest_pending_task = next_task_item
        new_order.save()

        # Update our ongoing job.
        ongoing_job.open_order = new_order
        ongoing_job.save()
