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
    Associate,
    Comment,
    Customer,
    Organization,
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    WorkOrderServiceFee,
    SkillSet,
    Tag
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
            payment_date = row_dict[12] # do not import this field!
            status = row_dict[13]
            comment_text = row_dict[14]
            follow_up_comment_text = row_dict[15]
            workmanship = row_dict[16]
            time_and_budget = row_dict[17]
            punctual = row_dict[18]
            professional = row_dict[19]
            refer = row_dict[20]

            # Status
            if status == 'assigned':
                status = WORK_ORDER_STATE.IN_PROGRESS
            if status == 'completed_and_paid':
                status = WORK_ORDER_STATE.COMPLETED_AND_PAID
            if status == 'completed_and_unpaid':
                status = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID

            # Convert the datetime.
            # local_birthdate = self.get_date_from_formatting1(birthdate)
            local_assign_date = self.get_date_from_formatting3(assign_date)
            local_payment_date = self.get_date_from_formatting3(payment_date)
            local_completion_date = self.get_date_from_formatting3(completion_date)

            if local_assign_date is None or local_assign_date == "":
                local_assign_date = milestone_date

            # Convert to money.
            local_service_fee = Money(0.00, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
            if service_fee:
                service_fee = service_fee.replace('$', '')
                service_fee = service_fee.replace('\'', '')
                service_fee = float(service_fee)
                local_service_fee = Money(service_fee, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
                # DEVELOPER NOTES:
                # - The "service_fee" is deprecated and will not be included.
                # - The "payment_date" is deprecated and will not be included.

            # Conver to integer.
            if hours is None:
                hourse = 0
            if hours is '':
                hours = 0
            hours = int(float(hours))

            # Boolean
            is_ongoing = True if is_ongoing == 1 else False

            # Generate our closing reason.
            closing_reason = 0
            closing_reason_other = None
            if status == WORK_ORDER_STATE.CANCELLED:
                closing_reason = 1
                if follow_up_comment_text:
                    closing_reason_other = follow_up_comment_text
                if comment_text:
                    closing_reason_other = comment_text
                if closing_reason_other is None:
                    closing_reason_other = "-"

            # Lookup the customer and process it if the customer exists.
            customer = Customer.objects.filter(id=int_or_none(customer_pk),).first()

            # Lookup the associate...
            associate = Associate.objects.filter(id=int_or_none(associate_pk),).first()

            # Begin processing...
            if customer and associate:
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
                        'state': status
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
