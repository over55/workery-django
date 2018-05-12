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
    # Comment,
    Customer,
    Organization,
    Order,
    # OrderComment,
    Tag
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_business_customer_csv "london" "/Users/bmika/Developer/over55/workery-django/workery/tenant_historic_etl/csv/prod_employer.csv"
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
            self.style.SUCCESS(_('Importing (Business) Customers at path: %(url)s ...') % {
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
                    #     self.style.SUCCESS(_('Importing (Business) Customer #%(id)s') % {
                    #         'id': i
                    #     })
                    # )

                    # Run the command for importing the data in our database.
                    self.run_import_from_dict(row_dict, i)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported (Business) Customers.'))
        )

    def run_import_from_dict(self, row_dict, index=1):
        try:
            # For debugging purposes.
            # print(row_dict)

            pk = row_dict[0]
            caller = row_dict[1]
            company = row_dict[2]
            pick = bool_or_none(row_dict[3]) #TODO: ???
            phone = row_dict[4]
            address = row_dict[5]
            city = row_dict[6]
            postal_code = row_dict[7]
            fax = row_dict[8]
            email = row_dict[9]
            com1 = row_dict[10]
            url = None

            # Minor formatting.
            email = email.replace(';', '')
            email = email.lower()
            address = '-' if address is '' else address
            address = '-' if address is None else address
            city = "London" if city is '' else city
            if "www" in email.lower():
                url = "http://"+email.lower()
                email = ""
            phone = phone.replace('(', '')
            phone = phone.replace(')', '')
            phone = phone.replace('-', '')
            phone = phone.replace(' ', '')
            phone = phone.replace('.', '')
            phone = int_or_none(phone)
            fax = fax.replace('(', '')
            fax = fax.replace(')', '')
            fax = fax.replace('-', '')
            fax = fax.replace(' ', '')
            fax = fax.replace('.', '')
            fax = int_or_none(fax)

            # Attempt to lookup or create user.
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
                    }
                )

            # Generate and assign the password.
            if created:
                user.set_password(get_random_string())
                user.save()

                # Attach our user to the "CUSTOMER_GROUP_ID"
                user.groups.add(CUSTOMER_GROUP_ID)

            # Format telephone number(s).
            if phone:
                phone = phonenumbers.parse(str(phone), "CA")
            if fax:
                fax = phonenumbers.parse(str(fax), "CA")


            # Insert our extracted data into our database.
            customer, create = Customer.objects.update_or_create(
                id=pk,
                defaults={
                    'owner': user,
                    'last_name':company,
                    'given_name':caller,
                    'telephone': phone,
                    'telephone_type_of': TELEPHONE_CONTACT_POINT_TYPE_OF_ID,
                    'postal_code': postal_code,
                    'street_address': address,
                    'address_locality': city,
                    'address_country': 'Canada',
                    'address_region': 'Ontario',
                    'email': email,
                    'fax_number': fax,
                    'description': com1,
                    'url': url,
                    'is_business': True,
                    'last_modified_by': None,
                    'created_by': None,
                    'type_of': COMMERCIAL_CUSTOMER_TYPE_OF_ID
                }
            )

            # Save the model.
            organization, create = Organization.objects.update_or_create(
                name=company,
                defaults={
                    'owner': customer.owner,
                    'name':company,
                    'type_of': UNKNOWN_ORGANIZATION_TYPE_OF_ID
                }
            )
            customer.organization = organization
            customer.save()


        except Exception as e:
            self.stdout.write(
                self.style.NOTICE(_('Importing (Business) Customer #%(id)s with exception "%(e)s".') % {
                    'e': str(e),
                    'id': str(pk)
                })
            )
