# -*- coding: utf-8 -*-
import csv
import os
import sys
import re
import os.path as ospath
import codecs
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedFranchise
from tenant_foundation.models import Staff
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
    SharedMe
)
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Customer,
    CustomerAffiliation,
    Organization
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_order_csv "london" "/Users/bmika/Developer/over55/overfiftyfive-django/overfiftyfive/tenant_historic_etl/static/prod_orders.csv"
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
                    self.run_import_from_dict(row_dict)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported order.csv file.'))
        )

    def begin_processing(self, franchise, csvfile):
        # FOR DEBUGGING PURPOSES ONLY. UNCOMMENT AT YOUR OWN RISK!
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # from tenant_foundation.models.customer import Customer
        # from tenant_foundation.models.associate import Associate
        # from django.contrib.auth.models import User
        # Customer.objects.delete_all()
        # Associate.objects.delete_all()
        # User.objects.all().delete()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.run_customer_importer_from_csv_file(franchise, csvfile)

    def run_import_from_dict(self, row_dict):
        try:
            # For debugging purposes.
            # print(row_dict)

            # Fetch our values.
            order_pk = int_or_none(row_dict[0])
            associate_pk = int_or_none(row_dict[1])
            associate_last_name = row_dict[2]
            assign_date = row_dict[3]
            customer_pk = int_or_none(row_dict[4])
            customer_first_name = row_dict[5]
            customer_last_name = row_dict[6]
            telephone = row_dict[7]
            telephone_extension = None
            postal_code = row_dict[8]
            learn_about = row_dict[9]
            is_support = True if row_dict[10] == "TRUE" else False
            is_senior = True if row_dict[11] == "TRUE" else False
            birthdate = row_dict[12]
            customer_email = row_dict[13]
            job_type = row_dict[14]
            is_ongoing = True if row_dict[15] == "TRUE" else False
            is_cancelled = True if row_dict[16] == "TRUE" else False
            date_done = row_dict[17]
            hours = row_dict[18]
            service_fee = row_dict[19]
            date_paid = row_dict[20]
            comment = row_dict[21]
            follow_up_comment = row_dict[22]
            workmanship = row_dict[23]
            time_and_budget = row_dict[24]
            punctual = row_dict[25]
            professional = row_dict[26]
            refer = row_dict[27]
            score = row_dict[28]
            url = None

            # Minor formatting for various fields.
            customer_email = customer_email.replace(';', '')
            customer_email = customer_email.replace(':', '')
            customer_email = customer_email.replace('NONE', '')
            customer_email = customer_email.replace('N/A', '')
            customer_email = customer_email.replace(' ', '')
            customer_email = customer_email.lower()
            # address = '-' if address is '' else address
            # address = '-' if address is None else address
            # city = "London" if city is '' else city
            if "www" in customer_email.lower():
                url = "http://"+customer_email.lower()
                customer_email = ""
            if "ext" in customer_email.lower():
                telephone_extension = customer_email
                customer_email = ""
            telephone = telephone.replace('(', '')
            telephone = telephone.replace(')', '')
            telephone = telephone.replace('-', '')
            telephone = telephone.replace(' ', '')
            telephone = telephone.replace('.', '')
            telephone = int_or_none(telephone)

            # Convert the datetime.
            local_birthdate = self.get_date_from_formatting1(birthdate)
            local_assign_date = self.get_date_from_formatting2(assign_date)
            local_date_done = self.get_date_from_formatting2(date_done)
            local_date_paid = self.get_date_from_formatting2(date_paid)

            # # For debugging purposes.
            # print(
            #     order_pk,
            #     associate_pk,
            #     associate_last_name,
            #     local_assign_date,
            #     customer_pk,
            #     customer_first_name,
            #     customer_last_name,
            #     telephone,
            #     postal_code,
            #     learn_about,
            #     is_support,
            #     is_senior,
            #     local_birthdate,
            #     customer_email,
            #     job_type,
            #     is_ongoing,
            #     is_cancelled,
            #     local_date_done,
            #     hours,
            #     service_fee,
            #     local_date_paid,
            #     comment,
            #     follow_up_comment,
            #     workmanship,
            #     time_and_budget,
            #     punctual,
            #     professional,
            #     refer,
            #     score
            # )

            # Attempt to lookup or create user based if we have an email.
            user = None
            if customer_email is not None:
                user = User.objects.filter(email=customer_email).first()
                if user is None:
                    # Create our user.
                    user = User.objects.create(
                        first_name=customer_first_name,
                        last_name=customer_last_name,
                        email=customer_email,
                        username=get_unique_username_from_email(customer_email),
                        is_active=True,
                    )

                    # Generate and assign the password.
                    user.set_password(get_random_string())
                    user.save()

                    # Attach our user to the "CUSTOMER_GROUP_ID"
                    user.groups.add(CUSTOMER_GROUP_ID)

            # Insert our extracted data into our database.
            customer, create = Customer.objects.update_or_create(
                id=int_or_none(customer_pk),
                defaults={
                    'id': customer_pk,
                    'owner': user,
                    'last_name': customer_last_name,
                    'given_name': customer_first_name,
                    # 'middle_name':middle_name,
                    'telephone': telephone,
                    'telephone_extension': telephone_extension,
                    'postal_code': postal_code,
                    'birthdate': local_birthdate,
                    # 'street_address': address,
                    # 'address_locality': city,
                    # 'address_country': 'Canada',
                    # 'address_region': 'Ontario',
                    'email': customer_email,
                    'join_date': local_assign_date,
                    # 'job_info_read': job_info_read,
                    'how_hear': learn_about,
                    # 'description': job_description,
                    'is_senior': bool(is_senior),
                    'is_support': bool(is_support)
                }
            )

        except Exception as e:
            if not "list index out of range" in str(e):
                print(e)

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
