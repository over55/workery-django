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
    AssociateComment,
    Associate,
    Comment,
    Customer,
    Organization
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_associate_csv "london" "/Users/bmika/Developer/over55/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv/prod_employee.csv"
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
            self.style.SUCCESS(_('Importing Associates at path: %(url)s ...') % {
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
                    #     self.style.SUCCESS(_('Importing Associate #%(id)s') % {
                    #         'id': i
                    #     })
                    # )

                    # Run the command for importing the data in our database.
                    self.run_import_from_dict(row_dict, i)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported Associates.'))
        )

    def run_import_from_dict(self, row_dict, index=1):
        try:
            # For debugging purposes.
            # print(row_dict)

            # Extract the data.
            pk = row_dict[0]                     # CLIENTNO
            last_name = row_dict[1]              # LNAME
            given_name = row_dict[2]             # GNAMES
            business = row_dict[3]               # BUSINESS
            middle_name = row_dict[4]            # MNAME
            is_active = row_dict[5]              # ACTIVE?
            birthdate = row_dict[6]              # BIRTHDATE
            address = row_dict[7]                # ADDRESS
            join_date = row_dict[8]              # DATE
            phone = row_dict[9]                  # PHONE
            fax = row_dict[10]                   # FAX
            cell = row_dict[11]                  # CELL
            email = row_dict[12]                 # E-MAIL
            city = row_dict[13]                  # CITY
            province = row_dict[14]              # PROV
            postal_code = row_dict[15]           # POSTCODE
            ldn_area = row_dict[16]              # LONDAREA
            hourly_salary_desired = row_dict[17] # HRLYSALDESIR
            limit_special = row_dict[18]         # LIMITSPECIAL
            dues_pd = row_dict[19]               # DUES PD
            ins_due = row_dict[20]               # INS DUE
            police_check = row_dict[21]          # POLCHK
            drivers_license_class = row_dict[22] # DRLICCLASS
            comments_text = row_dict[23]         # COMMENTS
            has_car = row_dict[24]               # Car?
            has_van = row_dict[25]               # Van?
            has_truck = row_dict[26]             # Truck?
            is_full_time = row_dict[27]          # Full Time
            is_part_time = row_dict[28]          # Part Time
            is_contract_time = row_dict[29]      # Contract
            is_small_job = row_dict[30]          # Small Jobs
            how_hear = row_dict[31]              # How Hear

            # Convert the datetime.
            local_birthdate = get_dt_from_toronto_timezone_ms_access_dt_string(birthdate)
            local_join_date = get_dt_from_toronto_timezone_ms_access_dt_string(join_date)
            local_dues_pd = get_dt_from_toronto_timezone_ms_access_dt_string(dues_pd)
            local_ins_due = get_dt_from_toronto_timezone_ms_access_dt_string(ins_due)
            local_police_check = get_dt_from_toronto_timezone_ms_access_dt_string(police_check)

            # Minor formatting.
            email = email.replace(';', '')
            email = email.replace(':', '')
            email = email.replace('NONE', '')
            email = email.replace('N/A', '')
            email = email.replace(' ', '')
            email = email.lower()
            address = '-' if address is '' else address
            address = '-' if address is None else address
            province = 'ON' if province is '' else province
            province = 'ON' if province is None else province
            city = "London" if city is '' else city
            fax = fax.replace('(', '')
            fax = fax.replace(')', '')
            fax = fax.replace('-', '')
            fax = fax.replace(' ', '')
            fax = fax.replace('.', '')

            phone = phone.replace('(', '')
            phone = phone.replace(')', '')
            phone = phone.replace('-', '')
            phone = phone.replace(' ', '')
            phone = phone.replace('.', '')

            cell = cell.replace('(', '')
            cell = cell.replace(')', '')
            cell = cell.replace('-', '')
            cell = cell.replace(' ', '')
            cell = cell.replace('.', '')

            # Convert is active to be python boolean.
            if is_active == '0':
                is_active = False
            if is_active == '1':
                is_active = True

            # Create or update our user.
            user = None
            created = False
            if email is not None:
                user, created = SharedUser.objects.update_or_create(
                    email=email,
                    defaults={
                        'first_name': given_name,
                        'last_name': last_name,
                        'email': email,
                        'is_active': is_active,
                    }
                )

            if created:
                # Generate and assign the password.
                user.set_password(get_random_string())
                user.save()

                # Attach our user to the "Executive"
                user.groups.add(ASSOCIATE_GROUP_ID)

            # Format telephone number(s).
            if phone:
                phone = phonenumbers.parse(str(phone), "CA")
            if cell:
                cell = phonenumbers.parse(str(cell), "CA")
            if fax:
                fax = phonenumbers.parse(str(fax), "CA")

            # Update or create.
            associate, created_associate = Associate.objects.update_or_create(
                id=pk,
                defaults={
                    'owner': user,
                    'last_name':last_name,
                    'given_name':given_name,
                    'business':business,
                    'middle_name':middle_name,
                    # 'is_active':bool_or_none(is_active),
                    'birthdate':local_birthdate,
                    'address_country':'Canada',
                    'join_date':local_join_date,
                    'telephone':phone,
                    'telephone_type_of': TELEPHONE_CONTACT_POINT_TYPE_OF_ID,
                    'other_telephone': cell,
                    'other_telephone_type_of': MOBILE_CONTACT_POINT_TYPE_OF_ID,
                    'fax_number':fax,
                    'email':email,
                    'address_locality':city,
                    'address_region':province,
                    'street_address': address,
                    'postal_code':postal_code,
                    'area_served':ldn_area,
                    'hourly_salary_desired':int_or_none(hourly_salary_desired),
                    'limit_special':limit_special,
                    'dues_pd':local_dues_pd,
                    'ins_due':local_ins_due,
                    'police_check':local_police_check,
                    'drivers_license_class':drivers_license_class,
                    # 'comments':comments,
                    'has_car':bool_or_none(has_van),
                    'has_van':bool_or_none(has_van),
                    'has_truck':bool_or_none(has_truck),
                    'is_full_time':bool_or_none(is_full_time),
                    'is_part_time':bool_or_none(is_part_time),
                    'is_contract_time':bool_or_none(is_contract_time),
                    'is_small_job':bool_or_none(is_small_job),
                    'how_hear':how_hear,
                    'last_modified_by': None,
                    'created_by': None,
                }
            )

            # Create our comments.
            comment, created_comment = Comment.objects.update_or_create(
                text=comments_text,
                defaults={
                    'text': comments_text
                }
            )
            AssociateComment.objects.update_or_create(
                about=associate,
                comment=comment,
                defaults={
                    'about': associate,
                    'comment': comment
                }
            )

            # For debugging purposes.
            # print(associate, create)

        except Exception as e:
            self.stdout.write(
                self.style.NOTICE(_('Importing Associate Member #%(id)s with exception "%(e)s" for %(email)s.') % {
                    'e': str(e),
                    'id': str(index),
                    'email': str(email)
                })
            )
