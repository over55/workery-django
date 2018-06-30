# -*- coding: utf-8 -*-
import phonenumbers
import csv
import os
import sys
import re
import os.path as ospath
import codecs
import datetime
import pytz
from decimal import *
from djmoney.money import Money
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedFranchise
from tenant_foundation.models import Staff
from djmoney.money import Money
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from shared_foundation.models import (
    SharedFranchise,
    SharedUser
)
from tenant_foundation.constants import *
from tenant_foundation.models import (
    ACTIVITY_SHEET_ITEM_STATE,
    ActivitySheetItem,
    Associate,
    Comment,
    Customer,
    Organization,
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    WorkOrderServiceFee,
    SkillSet,
    Tag,
    TaskItem
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_order_csv "london" "/Users/bmika/Developer/over55/workery-django/workery/tenant_historic_etl/csv/prod_orders.csv"
"""

# Get the native timezone that the database originally used.
toronto_timezone = pytz.timezone('America/Toronto')


class Command(BaseCommand):
    help = _('Command will load up historical data with tenant for the "orders.csv" file.')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('full_filepath', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get user inputs.
        schema_name = options['schema_name'][0]
        full_filepath = options['full_filepath'][0]

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Importing WorkOrders at path: %(url)s ...') % {
                'url': full_filepath
            })
        )

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        # Begin importing...
        with open(full_filepath, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i, row_dict in enumerate(csvreader):
                if i > 0:

                    # # Used for debugging purposes only.
                    # self.stdout.write(
                    #     self.style.SUCCESS(_('Importing WorkOrder #%(id)s') % {
                    #         'id': i
                    #     })
                    # )

                    # Begin importing...
                    self.run_import_from_dict(row_dict, i)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported WorkOrders.'))
        )

    def run_import_from_dict(self, row_dict, index):
        service_fee_obj = WorkOrderServiceFee.objects.get(id=1)

        milestone_date = datetime(2016, 12, 31, 23, 00)
        milestone_date = milestone_date.replace(tzinfo=toronto_timezone) # Make timezone aware.

        try:
            # For debugging purposes.
            # print(row_dict)

            # Fetch our values.
            order_pk = int_or_none(row_dict[0])
            customer_pk = int_or_none(row_dict[1])
            associate_pk = int_or_none(row_dict[3])
            is_home_support = int_or_none(row_dict[4])
            category = row_dict[5]
            assign_date = row_dict[6]
            is_ongoing = int_or_none(row_dict[7])
            is_cancelled = int_or_none(row_dict[8]) #skip
            completion_date = row_dict[9]
            hours = row_dict[10]
            service_fee = row_dict[11]
            payment_date = row_dict[12]
            status = row_dict[13]
            cancellation_reason = row_dict[14]
            comment_text = row_dict[15]
            inv_no = int_or_none(row_dict[16])
            follow_up_comment_text = row_dict[17]
            workmanship = int_or_none(row_dict[18])     # 1 / 5
            time_and_budget = int_or_none(row_dict[19]) # 2 / 5
            punctual = int_or_none(row_dict[20])        # 3 / 5
            professional = int_or_none(row_dict[21])    # 4 / 5
            refer = int_or_none(row_dict[22])           # 5 / 5

            # --- Status ---
            if status == 'assigned':
                status = WORK_ORDER_STATE.IN_PROGRESS
            if status == 'completed_and_paid':
                status = WORK_ORDER_STATE.COMPLETED_AND_PAID
            if status == 'completed_and_unpaid':
                status = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
            if status == 'completed_but_unpaid':
                status = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
            if status == 'complete_but_unpaid':
                status = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
            if status == 'complete_and_unpaid':
                status = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID

            # --- closing_reason / closing_reason_other ---
            closing_reason = 0
            closing_reason_other = None
            if status == WORK_ORDER_STATE.CANCELLED:
                closing_reason = 1
                #
                if cancellation_reason.lower() == "quote was too high":
                    closing_reason = 2
                elif cancellation_reason.lower() == "quote too high":
                    closing_reason = 2
                elif cancellation_reason.lower() == "job completed by someone else":
                    closing_reason = 3
                elif cancellation_reason.lower() == "job completed by associate":
                    closing_reason = 4
                elif cancellation_reason.lower() == "work no longer needed":
                    closing_reason = 5
                elif cancellation_reason.lower() == "client not satisfied with associate":
                    closing_reason = 6
                elif cancellation_reason.lower() == "client did work themselves":
                    closing_reason = 7
                elif cancellation_reason.lower() == "no associate available":
                    closing_reason = 8
                elif cancellation_reason.lower() == "work environment unsuitable":
                    closing_reason = 9
                elif cancellation_reason.lower() == "client did not return call":
                    closing_reason = 10
                elif cancellation_reason.lower() == "associate did not have necessary equipment":
                    closing_reason = 11
                elif cancellation_reason.lower() == "repair not possible":
                    closing_reason = 12
                elif cancellation_reason.lower() == "could not meet deadline":
                    closing_reason = 13
                elif cancellation_reason.lower() == "associate did not call client":
                    closing_reason = 14
                elif cancellation_reason.lower() == "member issue":
                    closing_reason = 15
                elif cancellation_reason.lower() == "client billing issue":
                    closing_reason = 16
                else:
                    if cancellation_reason is None or len(cancellation_reason) == 0:
                        closing_reason_other = "-"
                    else:
                        closing_reason_other = cancellation_reason

            # --- Score ---
            score = 0
            if workmanship is not None:
                score += workmanship
            else:
                workmanship = 0
            if time_and_budget is not None:
                score += time_and_budget
            else:
                time_and_budget = 0
            if punctual is not None:
                score += punctual
            else:
                punctual = 0
            if professional is not None:
                score += professional
            else:
                professional = 0
            if refer is not None:
                score += refer
            else:
                refer = 0

            # --- Convert the datetime ---
            local_assign_date = self.get_date_from_formatting3(assign_date)
            local_payment_date = self.get_date_from_formatting3(payment_date)
            local_completion_date = self.get_date_from_formatting3(completion_date)

            if local_assign_date is None or local_assign_date == "":
                local_assign_date = milestone_date

            # --- Convert to money ---
            local_service_fee = Money(0.00, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
            if service_fee:
                service_fee = service_fee.replace('$', '')
                service_fee = service_fee.replace('\'', '')
                service_fee = float(service_fee)
                local_service_fee = Money(service_fee, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
                # DEVELOPER NOTES:
                # - The "service_fee" is deprecated and will not be included.
                # - The "payment_date" is deprecated and will not be included.

            # --- Convert to integer ---
            if hours is None:
                hourse = 0
            if hours is '':
                hours = 0
            hours = int(float(hours))

            if inv_no is None:
                inv_no = 0

            # --- Boolean ---
            is_ongoing = True if is_ongoing == 1 else False

            # Lookup the customer and process it if the customer exists.
            customer = Customer.objects.filter(id=int_or_none(customer_pk),).first()

            # Lookup the associate...
            associate = Associate.objects.filter(id=int_or_none(associate_pk),).first()

            # Begin processing...
            if customer:
                order, create = WorkOrder.objects.update_or_create(
                    id=order_pk,
                    defaults={
                        'id': order_pk,
                        'customer': customer,
                        'associate': associate,
                        'assignment_date': local_assign_date,
                        'is_ongoing': is_ongoing,
                        'closing_reason': closing_reason,
                        'closing_reason_other': closing_reason_other,
                        'completion_date': local_completion_date,
                        'hours':  hours,
                        'last_modified_by': None,
                        'created_by': None,
                        'invoice_service_fee_payment_date': local_payment_date,
                        'invoice_service_fee': service_fee_obj,
                        'invoice_service_fee_amount': local_service_fee,
                        'type_of': RESIDENTIAL_JOB_TYPE_OF_ID, # WE PUT THIS BECAUSE WE ARE NOT IMPORTING COMMERCIAL!
                        'state': status,
                        'was_job_satisfactory': workmanship,
                        'was_job_finished_on_time_and_on_budget': time_and_budget,
                        'was_associate_punctual': punctual,
                        'was_associate_professional': professional,
                        'would_customer_refer_our_organization': refer,
                        'score': score,
                        'invoice_id': inv_no
                    }
                )

                # Add our start date.
                if local_assign_date:
                    order.start_date = local_assign_date
                    if local_completion_date:
                        order.completion_date = local_completion_date
                        if local_payment_date:
                            order.start_date = local_payment_date
                    order.save()

                # Added to tags.
                if category:
                    skill_set = SkillSet.objects.filter(sub_category=category).last()
                    if skill_set and order:
                        order.skill_sets.add(skill_set)

                # Add comments.
                if comment_text:
                    # Use an existing comment if it exists!
                    comment = Comment.objects.filter(text=comment_text).first()
                    if comment is None:
                        comment = Comment.objects.create(text=comment_text)

                    # Map user commment to job.
                    WorkOrderComment.objects.update_or_create(
                        about=order,
                        comment=comment,
                        defaults={
                            'about': order,
                            'comment': comment
                        }
                    )

                # Added follow up comment.
                if follow_up_comment_text:
                    # Use an existing follow up comment if it exists!
                    comment = Comment.objects.filter(text=follow_up_comment_text).first()
                    if comment is None:
                        comment = Comment.objects.create(text=follow_up_comment_text)

                    # Map user follow up commment to job.
                    WorkOrderComment.objects.update_or_create(
                        about=order,
                        comment=comment,
                        defaults={
                            'about': order,
                            'comment': comment
                        }
                    )

                # --- Completion status ---
                if status == WORK_ORDER_STATE.COMPLETED_AND_PAID and associate and local_completion_date:
                    ActivitySheetItem.objects.update_or_create(
                        job=order,
                        associate=associate,
                        defaults={
                            'job': order,
                            'associate': associate,
                            'comment': comment_text,
                            'state': ACTIVITY_SHEET_ITEM_STATE.ACCEPTED,
                            'created_at': local_completion_date,
                            'created_by': None,
                        }
                    )

                    # TaskItem.objects.update_or_create(
                    #     job=order,
                    #     defaults={
                    #         'type_of': FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                    #         'title': _('Completion Survey'),
                    #         'description': _('Please call up the client and perform the satisfaction survey.'),
                    #         'due_date': timezone.now(),
                    #         'is_closed': True,
                    #         'job': order,
                    #         'created_at': local_completion_date,
                    #         'created_by': None,
                    #         'created_from': '127.0.0.1',
                    #         'created_from_is_public': False,
                    #         'last_modified_by': None
                    #     }
                    # )

                # if status == WORK_ORDER_STATE.COMPLETED_BUT_UNPAID:
                #     TaskItem.objects.update_or_create(
                #         job=order,
                #         defaults={
                #             'type_of': FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                #             'title': _('Completion Survey'),
                #             'description': _('Please call up the client and perform the satisfaction survey.'),
                #             'due_date': timezone.now(),
                #             'is_closed': False,
                #             'job': order,
                #             'created_at': timezone.now(),
                #             'created_by': None,
                #             'created_from': '127.0.0.1',
                #             'created_from_is_public': False,
                #             'last_modified_by': None
                #         }
                #     )

                if status == WORK_ORDER_STATE.IN_PROGRESS:
                    TaskItem.objects.update_or_create(
                        job=order,
                        defaults={
                            'type_of': FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                            'title': _('Completion Survey'),
                            'description': _('Please call up the client and perform the satisfaction survey.'),
                            'due_date': timezone.now(),
                            'is_closed': False,
                            'job': order,
                            'created_at': timezone.now(),
                            'created_by': None,
                            'created_from': '127.0.0.1',
                            'created_from_is_public': False,
                            'last_modified_by': None
                        }
                    )

        except Exception as e:
            self.stdout.write(
                self.style.NOTICE(_('Importing WorkOrder #%(id)s with exception "%(e)s".') % {
                    'e': str(e),
                    'id': str(index)
                })
            )


    def get_date_from_formatting1(self, birthdate):
        """
        Format `5/15/48` to '1948-05-15'.
        """
        if birthdate:
            arr = birthdate.split("/")
            year = "19"+arr[2]
            day = arr[1]
            month = arr[0]
            dt_string = year+"-"+month+"-"+day
            dt = get_utc_dt_from_toronto_dt_string(dt_string)
            return dt
        return None

    def get_date_from_formatting2(self, assign_date):
        """
        Format `'01-Dec-17` to '2017-Dec-01'.
        """
        if assign_date:
            arr = assign_date.split("-")
            year = "20"+arr[2]
            day = arr[0]
            month = arr[1]
            dt_string = year+"-"+month+"-"+day
            dt = get_utc_dt_from_toronto_dt_string(dt_string)
            return dt
        return None

    def get_date_from_formatting3(self, assign_date):
        """
        Format `'01-Dec-17` to '2017-Dec-01'.
        """
        if assign_date:
            arr = assign_date.split("-")
            year = arr[0]
            day = arr[2]
            month = arr[1]
            dt_string = year+"-"+month+"-"+day
            dt = get_utc_dt_from_toronto_dt_string(dt_string)
            return dt
        return None
