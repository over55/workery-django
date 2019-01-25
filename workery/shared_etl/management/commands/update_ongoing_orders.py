# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from dateutil import tz, relativedelta
from decimal import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from django_tenants.utils import tenant_context

from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from shared_foundation.utils import get_end_of_date_for_this_dt, get_first_date_for_this_dt
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


class Command(BaseCommand): #TODO: UNIT TEST
    """
    python manage.py update_ongoing_orders
    """
    help = _('ETL will iterate through all ongoing jobs in all tenants to create an associated pending task to review by staff.')

    def handle(self, *args, **options):
        franchises = SharedFranchise.objects.filter(
            ~Q(schema_name="public") &
            ~Q(schema_name="test")
        )

        # Iterate through all the franchise schemas and perform our operations
        # limited to the specific operation.
        for franchise in franchises.all():
            with tenant_context(franchise):
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
        now_dt = franchise.get_todays_date_plus_days()
        now_d = now_dt.date()
        for ongoing_job in ongoing_jobs.all():
            self.process_ongoing_work_order(ongoing_job, now_d)

    def process_ongoing_work_order(self, ongoing_job, now_d):
        """
        Function will:
        (1) At first of month, if not cancelled (master form aka cancelled) then:
        (a) Create a new job.
        (b) Starts job as “In Progress”.
        (c) From the GUI perspective, make sure all the screens display “In Progress / Ongoing” to make the system more usable.
        (d) This job has NO TASKS created.
        (e) Send email to the staff.
        (2) At last day of month, 12:00AM, the ongoing job becomes “completed but unpaid”.
        """
        # Generate the following dates based on today's date.
        first_day_dt = get_first_date_for_this_dt(now_d)
        last_day_dt = get_end_of_date_for_this_dt(now_d)

        # Get the latest work order.
        work_orders = ongoing_job.work_orders.filter(created__range=[first_day_dt, last_day_dt])
        print(work_orders)

        # If today is the first of the month then we will:
        # (1) Create a new job
        # (2) Make the new job be "In Progress".
        if now_d is first_day_dt:
            print("Today is first of month.")

        # If today is the end of the month then we will:
        # (1) Close the existing job.
        if now_d is last_day_dt:
            print("Today is end of month.")

        # work_orders = ongoing_job.work_orders.all()
        #
        # print(ongoing_job)
        # print(work_orders)
        # print()
