# -*- coding: utf-8 -*-
import phonenumbers
import csv
import os
import sys
import re
import os.path as ospath
import codecs
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
    Order,
    OrderComment,
    SkillSet,
    Tag
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_order_csv "london" "/Users/bmika/Developer/over55/workery-django/workery/tenant_historic_etl/csv/prod_orders.csv"
"""


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
            self.style.SUCCESS(_('Importing Orders at path: %(url)s ...') % {
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
                    #     self.style.SUCCESS(_('Importing Order #%(id)s') % {
                    #         'id': i
                    #     })
                    # )

                    # Begin importing...
                    self.run_import_from_dict(row_dict, i)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported Orders.'))
        )

    def run_import_from_dict(self, row_dict, index):
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
            is_ongoing = row_dict[7]
            is_cancelled = row_dict[8]
            completion_date = row_dict[9]
            hours = row_dict[10]
            service_fee = row_dict[11]
            payment_date = row_dict[12]
            comment_text = row_dict[13]
            follow_up_comment_text = row_dict[14]
            time_and_budget = row_dict[15]
            time_and_budget = row_dict[16]
            punctual = row_dict[17]
            professional = row_dict[18]
            refer = row_dict[19]

            # # Convert the datetime.
            # local_birthdate = self.get_date_from_formatting1(birthdate)
            local_assign_date = self.get_date_from_formatting2(assign_date)
            local_payment_date = self.get_date_from_formatting2(payment_date)
            local_completion_date = self.get_date_from_formatting2(completion_date)

            # Convert to money.
            local_service_fee = Money(0.00, O55_APP_DEFAULT_MONEY_CURRENCY)
            if service_fee:
                service_fee = service_fee.replace('$', '')
                service_fee = service_fee.replace('\'', '')
                service_fee = float(service_fee)
                local_service_fee = Money(service_fee, O55_APP_DEFAULT_MONEY_CURRENCY)

            # Conver to integer.
            if hours is None:
                hourse = 0
            if hours is '':
                hours = 0
            hours = int(float(hours))

            # Boolean
            is_ongoing = True if is_ongoing == 1 else False
            is_cancelled = True if is_cancelled == 1 else False

            # Lookup the customer and process it if the customer exists.
            customer = Customer.objects.filter(id=int_or_none(customer_pk),).first()

            # Lookup the associate...
            associate = Associate.objects.filter(id=int_or_none(associate_pk),).first()

            # Begin processing...
            if customer and associate:
                order, create = Order.objects.update_or_create(
                    id=order_pk,
                    defaults={
                        'id': order_pk,
                        'customer': customer,
                        'associate': associate,
                        'assignment_date': local_assign_date,
                        'is_ongoing': is_ongoing,
                        'is_cancelled': is_cancelled,
                        'completion_date': local_completion_date,
                        'hours':  hours,
                        'service_fee': local_service_fee,
                        'payment_date': local_payment_date,
                        'last_modified_by': None,
                        'created_by': None,
                    }
                )

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
                    OrderComment.objects.update_or_create(
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
                    OrderComment.objects.update_or_create(
                        about=order,
                        comment=comment,
                        defaults={
                            'about': order,
                            'comment': comment
                        }
                    )

        except Exception as e:
            self.stdout.write(
                self.style.NOTICE(_('Importing Order #%(id)s with exception "%(e)s".') % {
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
