# -*- coding: utf-8 -*-
import phonenumbers
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
    CustomerComment,
    Organization,
    WorkOrder,
    WorkOrderComment,
    Tag
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_personal_customer_csv "london" "/Users/bmika/Developer/over55/workery-django/workery/tenant_historic_etl/csv/prod_small_job_employers.csv"
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
            self.style.SUCCESS(_('Importing (Personal) Customers at path: %(url)s ...') % {
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

        # # For debugging purposes only.
        # Customer.objects.delete_all()

        # Begin importing...
        with open(full_filepath, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i, row_dict in enumerate(csvreader):
                if i > 0:
                    # # Used for debugging purposes only.
                    # self.stdout.write(
                    #     self.style.SUCCESS(_('Importing (Personal) Customer #%(id)s') % {
                    #         'id': i
                    #     })
                    # )

                    # Run the command for importing the data in our database.
                    self.run_import_from_dict(row_dict, i)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported (Personal) Customers.'))
        )

    def run_import_from_dict(self, row_dict, index=1):
        try:
            # Fetch our values.
            pk = int_or_none(row_dict[0])
            project_date = row_dict[1]
            last_name = row_dict[2]
            first_name = row_dict[3]
            home_phone = row_dict[4]
            postal_code = row_dict[5]
            job_info_read = row_dict[6]
            learn_about = row_dict[7]
            is_support = bool_or_none(row_dict[8])
            is_senior = bool_or_none(row_dict[9])
            birthdate = row_dict[10]
            job_description = row_dict[11]
            address = row_dict[12]
            city = row_dict[13]
            email = row_dict[14]
            url = None
            telephone_extension = None

            # Minor formatting.
            email = email.replace(';', '')
            email = email.replace(':', '')
            email = email.replace('NONE', '')
            email = email.replace('N/A', '')
            email = email.replace(' ', '')
            email = email.lower()
            address = '-' if address is '' else address
            address = '-' if address is None else address
            city = "London" if city is '' else city
            if "www" in email.lower():
                url = "http://"+email.lower()
                email = ""
            if "ext" in email.lower():
                telephone_extension = email
                email = ""
            home_phone = home_phone.replace('(', '')
            home_phone = home_phone.replace(')', '')
            home_phone = home_phone.replace('-', '')
            home_phone = home_phone.replace(' ', '')
            home_phone = home_phone.replace('.', '')
            home_phone = int_or_none(home_phone)

            # Convert the datetime.
            local_birthdate = get_utc_dt_from_toronto_dt_string(birthdate)
            local_project_date = get_utc_dt_from_toronto_dt_string(project_date)

            # Finally title the words.
            if first_name:
                first_name = first_name.title()
            if last_name:
                last_name = last_name.title()
            if address:
                address = address.title()
            if city:
                city = city.title()

            # Create or update our user if it exists
            user = None
            email = None
            created = False
            if email is not None and email != "":
                user, created = SharedUser.objects.update_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_active': True,
                        'date_joined': local_project_date
                    }
                )

            if created:
                # Generate and assign the password.
                user.set_password(get_random_string())
                user.save()

                # Attach our user to the "CUSTOMER_GROUP_ID"
                user.groups.add(CUSTOMER_GROUP_ID)

            # Format telephone number.
            if home_phone:
                home_phone = phonenumbers.parse(str(home_phone), "CA")

            # Insert our extracted data into our database.
            customer, create = Customer.objects.update_or_create(
                id=pk,
                defaults={
                    'id': pk,
                    'owner': user,
                    'last_name':last_name,
                    'given_name':first_name,
                    # 'middle_name':middle_name,
                    'telephone': home_phone,
                    'telephone_extension': telephone_extension,
                    'telephone_type_of': TELEPHONE_CONTACT_POINT_TYPE_OF_ID,
                    'postal_code': postal_code,
                    'birthdate': local_birthdate,
                    'street_address': address,
                    'address_locality': city,
                    'address_country': 'Canada',
                    'address_region': 'Ontario',
                    'email': email,
                    'join_date': local_project_date,
                    'job_info_read': job_info_read,
                    'how_hear': learn_about,
                    'description': job_description,
                    'is_senior': bool(is_senior),
                    'is_support': bool(is_support),
                    'is_business': False,
                    'last_modified_by': None,
                    'created_by': None,
                    'type_of': RESIDENTIAL_CUSTOMER_TYPE_OF_ID,
                    'is_ok_to_email': False,
                    'is_ok_to_text': False

                }
            )

            # For debugging purposes only.
            # self.stdout.write(
            #     self.style.SUCCESS(_('Imported (Personal) Customer #%(id)s.') % {
            #         'id': str(index)
            #     })
            # )

        except Exception as e:
            self.stdout.write(
                self.style.NOTICE(_('Importing (Personal) Customer #%(id)s with exception "%(e)s" for %(email)s.') % {
                    'e': str(e),
                    'id': str(index),
                    'email': str(email)
                })
            )

            if "Your email is not unique!" in str(e):
                customer = Customer.objects.filter(email=email)
                print(customer)
                print()
