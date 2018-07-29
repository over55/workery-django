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
    help = _('ETL will iterate through all ongoing jobs in all tenants to create an associated pending task to review by staff.')

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
        ongoing_jobs = OngoingWorkOrder.objects.filter(state=ONGOING_WORK_ORDER_STATE.RUNNING).order_by('-id')
        for ongoing_job in ongoing_jobs.all():
            self.process_ongoing_work_order(ongoing_job)

    def process_ongoing_work_order(self, ongoing_job):
        """
        Function will:
        (1) Fetch the last job in from the ongoing job master form and create a
            new pending task.
        """
        latest_order = WorkOrder.objects.filter(ongoing_work_order=ongoing_job).order_by('-id').first()
        if latest_order:
            self.create_pending_task(latest_order, ongoing_job)

    def create_pending_task(self, latest_job, ongoing_job):
        # Create our new task for following up.
        next_task_item = TaskItem.objects.create(
            type_of = UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID,
            title = _('Ongoing Job Update'),
            description = _('Please review an ongoing job and process it.'),
            due_date = get_todays_date_plus_days(0),
            is_closed = False,
            job = latest_job
        )

        # Attach our pending task to our latest job
        latest_job.latest_pending_task = next_task_item
        latest_job.save()

        # Attach our pending task to our ongoing job master form.
        ongoing_job.latest_pending_task = next_task_item
        ongoing_job.save()
