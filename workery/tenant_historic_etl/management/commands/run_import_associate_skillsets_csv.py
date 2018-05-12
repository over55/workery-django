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
    Organization,
    SkillSet
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_import_associate_skillsets_csv "london" "/Users/bmika/Developer/over55/workery-django/workery/tenant_historic_etl/csv/prod_associate_to_skillsets.csv"
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
            self.style.SUCCESS(_('Successfully imported Associate skill sets.'))
        )

    def run_import_from_dict(self, row_dict, index=1):
        # ID #
        try:
            # For debugging purposes.
            # print(row_dict)

            # Extract the data.
            associate_id = row_dict[0]          # Associate ID
            first_name = row_dict[1]            # First Name
            last_name = row_dict[2]             # Last Name
            skill_set_names = row_dict[3]       # Skill Sets
            skill_set_ids = row_dict[4]         # Skill ID

            # Lookup the associate based on the `PK`.
            assocaite = Associate.objects.get(id=associate_id)

            # Split the IDs by comma.
            skill_set_ids_arr = skill_set_ids.split(',')

            # Iterate through all the skill sets.
            for skill_set_id in skill_set_ids_arr:
                skill_set_id = int(skill_set_id)
                skill_set = SkillSet.objects.get(id=skill_set_id)

                # Attach `SkillSet` objects to `Associate`.
                assocaite.skill_sets.add(skill_set)

            # self.stdout.write(
            #     self.style.SUCCESS(_('Imported Associate Member #%(id)s with SkillSets of "%(ids)s".') % {
            #         'id': str(associate_id),
            #         'ids': skill_set_ids_arr
            #     })
            # )

        except Exception as e:
            self.stdout.write(
                self.style.NOTICE(_('Importing Associate Member #%(id)s with exception "%(e)s".') % {
                    'e': str(e),
                    'id': associate_id
                })
            )
