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
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # EMAILER: HTML to TXT
from django.utils.text import Truncator
from django_tenants.utils import tenant_context

from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from shared_foundation.models import SharedUser
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

    (1)

    Example:
    python manage.py update_ongoing_orders
    """
    help = _('DEPRECATED ETL will iterate through all ongoing jobs in all tenants to create an associated pending task to review by staff.')

    def handle(self, *args, **options):
        franchises = SharedFranchise.objects.filter(
            ~Q(schema_name="public") &
            ~Q(schema_name="test")
        )

        # Iterate through all the franchise schemas and perform our operations
        # limited to the specific operation.
        for franchise in franchises.all():
            with tenant_context(franchise):
                self.run_update_all_ongoing_jobs_for_franchise(franchise)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all ongoing job orders.'))
        )

    def run_update_all_ongoing_jobs_for_franchise(self, franchise):
        """
        Function will iterate through all the `running` ongoing work orders and
        perform the necessary operations.
        """
        # Generate the following dates based on today's date.
        now_dt = franchise.get_todays_date_plus_days()
        now_d = now_dt.date()
        first_day_d = get_first_date_for_this_dt(now_d)
        last_day_d = get_end_of_date_for_this_dt(now_d)

        # # For debugging purposes only.
        # print("franchise", str(franchise), "\nnow_dt", now_dt, "\nnow_d", now_d)
        # print("first_day_d", first_day_d)
        # print("last_day_d", last_day_d, "\n")

        # If today is the first day of the month then we will close the existing job.
        if now_d == first_day_d:
        # if True:
            self.process_running_ongoing_jobs(now_dt)
        else:
            self.stdout.write(
                self.style.SUCCESS(_('Today is not first of month for the %(f_name)s organization.')%{
                    'f_name': str(franchise.name)
                })
            )

    @transaction.atomic
    def process_running_ongoing_jobs(self, now_dt):
        self.stdout.write(
            self.style.SUCCESS(_('Begin processing first day of month ongoing jobs...'))
        )

        # Variable used to track all the jobs which have been closed/created.
        closed_job_ids_arr = []
        created_job_ids_arr = []

        # STEP 1: Iterate through all the ongoing jobs which are `running`.
        ongoing_jobs = OngoingWorkOrder.objects.filter(
            state=ONGOING_WORK_ORDER_STATE.RUNNING
        ).order_by('-id')
        for ongoing_job in ongoing_jobs.all():

            # STEP 2: Find all the open work orders belonging to the ongoing job.
            jobs = ongoing_job.work_orders.filter(
                ~Q(associate=None)&
                ~Q(state=None)&
                ~Q(state=WORK_ORDER_STATE.DECLINED)&
                ~Q(state=WORK_ORDER_STATE.CANCELLED)&
                ~Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID)&
                ~Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)&
                ~Q(state=WORK_ORDER_STATE.ARCHIVED)
            )

            # STEP 3: Iterate through all the work orders and close them.
            for job in jobs.all():
                job.closing_reason = 4
                job.closing_reason_other = "Modified by ETL."
                job.completion_date = now_dt
                job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
                job.last_modified_by = None
                job.last_modified_from = None
                job.last_modified_from_is_public = False
                job.save()

                # STEP 4: Iterate through all the tasks and close them.
                task_items = job.task_items
                for task_item in task_items.all():
                    task_item.is_closed = True
                    task_item.last_modified_by = None
                    task_item.last_modified_from = None
                    task_item.last_modified_from_is_public = False
                    task_item.save()

                # STEP 5: Save the job ID of the job we modified to keep track that
                #         we modified these ongoing jobs.
                closed_job_ids_arr.append(job.id)

        self.stdout.write(
            self.style.SUCCESS(_('Finished closing first day of month ongoing jobs with IDs: %(arr)s.')%{
                'arr': str(closed_job_ids_arr)
            })
        )

        # STEP 6: Iterate through the `runnnig` ongoing jobs again.
        ongoing_jobs = OngoingWorkOrder.objects.filter(
            state=ONGOING_WORK_ORDER_STATE.RUNNING
        ).order_by('-id')
        for ongoing_job in ongoing_jobs.all():

            # STEP 7: Find the previously completion_date work order belonging
            #         to our ongoing job.
            previous_job = ongoing_job.work_orders.filter(
                Q(is_ongoing=True)&
                Q(
                    Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID)|
                    Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID)
                )&
                ~Q(associate=None) &
                ~Q(state=None)
            ).order_by('-completion_date').first()

            if previous_job is not None:

                # DEVELOPERS NOTE:
                # We will need to create a new start date which will essentially
                # be the starting date of next month.
                new_start_dt = now_dt + timedelta(days=1)

                # STEP 8: Clone our new work order. Please note function will
                #         include cloning related fields like `ManyToMany`
                #         fields.
                job = previous_job.clone()

                # STEP 9: Changed the specific dates.
                job.assignment_date = new_start_dt
                job.completion_date = new_start_dt
                job.save()

                # STEP 11: Save the job ID of the job we modified to keep track
                #         that we modified these ongoing jobs.
                created_job_ids_arr.append(job.id)

                self.stdout.write(
                    self.style.SUCCESS(_('Cloned job #: %(job_id)s.')%{
                        'job_id': str(job.id)
                    })
                )

        self.stdout.write(
            self.style.SUCCESS(_('Finished creating first day of month ongoing jobs with IDs: %(arr)s.')%{
                'arr': str(created_job_ids_arr)
            })
        )

        # STEP 11: Email the management staff that the following ongoing jobs
        #          were automatically modified by this ETL.
        if len(created_job_ids_arr) > 0:
            try:
                self.send_staff_an_email(
                    closed_job_ids_arr,
                    created_job_ids_arr, now_dt
                )
            except Exception as e:
                print("process_running_ongoing_jobs | e:",e)

        # DEVELOPERS NOTE:
        # PLEASE DO NOT DELETE THIS COMMENT. IF YOU WANT TO RUN MANUAL TESTS
        # ON THIS ETL THEN UNCOMMENT THIS CODE. THIS FUNCTION IS INSIDE THE
        # `TRANSACTION` METHOD SO THIS EXCEPTION WILL CAUSE THE DATABASE TO
        # REJECT OUR SUBMISSION.
        # raise Exception("Programmer halted")

    def send_staff_an_email(self, closed_job_ids_arr, created_job_ids_arr, now_dt):
        """
        The following code will send an email to the staff about the
        ongoing jobs which have been processed by our ETL.
        """
        subject = "WORKERY: Updated Ongoing Job(s)"
        param = {
            'tenant_todays_date': now_dt,
            'closed_job_ids_arr': closed_job_ids_arr,
            'created_job_ids_arr': created_job_ids_arr,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('shared_etl/email/update_ongoing_job_view.txt', param)
        # html_content = render_to_string('shared_auth/email/update_ongoing_job_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = SharedUser.get_management_staff_emails()

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        # msg.attach_alternative(html_content, "text/html")
        msg.send()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('Sent emails to: %(emails)s.')%{
                'emails': str(to)
            })
        )
