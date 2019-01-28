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
from tenant_foundation.models.staff import Staff


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
        # Generate the following dates based on today's date.
        now_dt = franchise.get_todays_date_plus_days()
        now_d = now_dt.date()
        first_day_dt = get_first_date_for_this_dt(now_d)
        last_day_dt = get_end_of_date_for_this_dt(now_d)

        # If today is the end of the month then we will:
        # (1) Close the existing job.
        if now_d == last_day_dt:
            self.process_last_day_of_month_ongoing_work_order(now_d)

        # If today is the first of the month then we will:
        # (1) Create a new job
        # (2) Make the new job be "In Progress".
        if now_d == first_day_dt:
            self.process_first_day_of_month_ongoing_work_order(now_d)

    def process_last_day_of_month_ongoing_work_order(self, now_d):
        """
        At last day of month, 12:00AM, the ongoing job becomes “completed but unpaid”.
        """
        self.stdout.write(
            self.style.SUCCESS(_('Begin processing last day of month ongoing jobs...'))
        )

        # Variable used to track all the jobs which have been updated.
        processed_job_ids_arr = []

        # STEP 1: Iterate through all the ongoing jobs which are running and
        #         close all the jobs inside that ongoing job which have not been
        #         completed.
        ongoing_jobs = OngoingWorkOrder.objects.filter(
            state=ONGOING_WORK_ORDER_STATE.RUNNING
        ).order_by('-id')
        for ongoing_job in ongoing_jobs.all():
            jobs = ongoing_job.work_orders.filter(
                state=WORK_ORDER_STATE.ONGOING
            )
            for job in jobs.all():
                # STEP 2: Close any ongoing jobs and set them to be completed
                #         but unpaid.
                job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
                job.last_modified_by = None
                job.last_modified_from = None
                job.last_modified_from_is_public = False
                job.save()

                # STEP 3: Save the job ID of the job we modified to keep track that
                #         we modified these ongoing jobs.
                processed_job_ids_arr.append(job.id)

        self.stdout.write(
            self.style.SUCCESS(_('Finished processing last day of month ongoing jobs with IDs: %(arr)s.')%{
                'arr': str(processed_job_ids_arr)
            })
        )

        # STEP 4: Email the management staff that the following ongoing jobs
        #         were automatically modified by this ETL.
        management_staffs = Staff.objects.filter_by_management_group()
        for management_staff in management_staffs.all():
            print("EMAIL: %(email)s"%{
                'email': str(management_staff.email)
            })

    def process_first_day_of_month_ongoing_work_order(self, now_d):
        """
        (1) At first of month, if not cancelled (master form aka cancelled) then:
        (a) Create a new job.
        (b) Starts job as “In Progress”.
        (c) From the GUI perspective, make sure all the screens display “In Progress / Ongoing” to make the system more usable.
        (d) This job has NO TASKS created.
        (e) Send email to the staff.
        """
        print("Today is first of month.")
        #
        # # STEP 1: Iterate through all the ongoing jobs which are running and
        # #         close all the jobs inside that ongoing job which have not been
        # #         completed.
        # ongoing_jobs = OngoingWorkOrder.objects.filter(
        #     state=ONGOING_WORK_ORDER_STATE.RUNNING
        # ).order_by('-id')
        # for ongoing_job in ongoing_jobs.all():
        #     jobs = ongoing_job.work_orders.filter(
        #         state=WORK_ORDER_STATE.ONGOING
        #     )
        #     for job in jobs.all():
        #         print(ongoing_job, "|", job)
