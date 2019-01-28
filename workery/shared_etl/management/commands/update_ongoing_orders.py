# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from dateutil import tz, relativedelta
from decimal import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.db import connection # Used for django tenants.
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # EMAILER: HTML to TXT
from django_tenants.utils import tenant_context

from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from shared_foundation.utils import get_end_of_date_for_this_dt, get_first_date_for_this_dt
from tenant_foundation import constants
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
    Description:
    Command will iterate through all the ongoing jobs (which are running) and
    perform the following:

    (1) At first of month, if not cancelled (master form aka cancelled) then:
    (a) Create a new job.
    (b) Starts job as “Ongoing”.
    (c) From the GUI perspective, make sure all the screens display “Ongoing”
        to make the system more usable.
    (d) This job has NO TASKS created.
    (e) Send email to the management staff.

    (2) At last day of month, 12:00AM, the ongoing job becomes “completed but
        unpaid” and send email to management staff.

    Example:
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

    def send_staff_an_email(self, staff, processed_job_ids_arr, now_d):
        work_orders = WorkOrder.objects.filter(id__in=processed_job_ids_arr)
        subject = "WORKERY: Updated Ongoing Job(s)"
        param = {
            'tenant_todays_date': now_d,
            'work_orders': work_orders,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('shared_etl/email/update_ongoing_job_view.txt', param)
        # html_content = render_to_string('shared_auth/email/update_ongoing_job_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [staff.email]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        # msg.attach_alternative(html_content, "text/html")
        msg.send()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('Sent email to: %(email)s.')%{
                'email': str(staff.email)
            })
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
        At last day of month, 12:00AM, the ongoing job becomes “completed but
        unpaid” and send email to management staff.
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
                job.closing_reason = 4
                job.closing_reason_other = "Modified by ETL."
                job.completion_date = now_d
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
            self.send_staff_an_email(management_staff, processed_job_ids_arr, now_d)

    def process_first_day_of_month_ongoing_work_order(self, now_d):
        """
        At first of month, if not cancelled (master form aka cancelled) then:
        (a) Create a new job.
        (b) Starts job as “Ongoing”.
        (c) From the GUI perspective, make sure all the screens display “In Progress / Ongoing” to make the system more usable.
        (d) This job has NO TASKS created.
        (e) Send email to the management staff.
        """
        self.stdout.write(
            self.style.SUCCESS(_('Begin processing first day of month ongoing jobs...'))
        )

        # Variable used to track all the jobs which have been updated.
        processed_job_ids_arr = []

        # STEP 1: Iterate through all the ongoing jobs which are running and
        #         close all the jobs inside that ongoing job which have been
        #         completed.
        ongoing_jobs = OngoingWorkOrder.objects.filter(
            state=ONGOING_WORK_ORDER_STATE.RUNNING
        ).order_by('-id')
        for ongoing_job in ongoing_jobs.all():
            # STEP 2: Find the previously completion_date ongoing job.
            previous_job = ongoing_job.work_orders.filter(
                is_ongoing=True
            ).order_by('-completion_date').first()

            # STEP 3: Create a new job for THIS month based on the previous
            #         months job.
            job = WorkOrder.objects.create(
                customer = previous_job.customer,
                associate = previous_job.associate,
                description = previous_job.description,
                assignment_date = previous_job.assignment_date,
                is_ongoing = True,
                is_home_support_service = previous_job.is_home_support_service,
                start_date = previous_job.start_date,
                completion_date = None,
                hours = previous_job.hours,
                type_of = previous_job.type_of,
                indexed_text = previous_job.indexed_text,
                latest_pending_task = None,
                state = WORK_ORDER_STATE.ONGOING,
                was_survey_conducted = False,
                was_there_financials_inputted = False,
            )

            # STEP 4: Save many-to-many fields from the previous months job.
            job.tags.set(previous_job.tags.all())
            job.skill_sets.set(previous_job.skill_sets.all())
            for activity_sheet in previous_job.activity_sheet.all():
                ActivitySheetItem.objects.create(
                    job = job,
                    ongoing_job = ongoing_job,
                    associate = previous_job.associate,
                    comment = "Automatically accepted by as ongoing job by ETL.",
                    state = ACTIVITY_SHEET_ITEM_STATE.ACCEPTED
                )

            # STEP 3: Save the job ID of the job we modified to keep track that
            #         we modified these ongoing jobs.
            processed_job_ids_arr.append(job.id)

        self.stdout.write(
            self.style.SUCCESS(_('Finished processing last day of month ongoing jobs with IDs: %(arr)s.')%{
                'arr': str(processed_job_ids_arr)
            })
        )

        # STEP 5: Email the management staff that the following ongoing jobs
        #         were automatically modified by this ETL.
        management_staffs = Staff.objects.filter_by_management_group()
        for management_staff in management_staffs.all():
            self.send_staff_an_email(management_staff, processed_job_ids_arr, now_d)
