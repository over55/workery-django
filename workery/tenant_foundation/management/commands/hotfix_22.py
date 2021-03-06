# -*- coding: utf-8 -*-
from freezegun import freeze_time
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    InsuranceRequirement,
    Organization,
    WorkOrder,
    # WorkOrderComment,
    WorkOrderServiceFee,
    ResourceCategory,
    ResourceItem,
    ResourceItemSortOrder,
    SkillSet,
    Staff,
    Tag,
    VehicleType
)
from tenant_foundation.constants import *


male_names_arr = [
"Michael",
"Mike",
"David",
"Dave",
"Robert",
"Bob",
"Jason",
"Jay",
"James",
"Jim",
"Christopher",
"Chris",
"John",
"Jack",
"Richard",
"Rick",
"Kevin",
"Matthew",
"Mark",
"Luke",
"Steven",
"Steve",
"Scott",
"Will",
"William",
"Bill",
"Brian",
"Paul",
"Darren",
"Daniel",
"Kenneth",
"Dan",
"Sean",
"Ken",
"Andrew"
]

female_names_arr = [
"Lisa",
"Michelle",
"Jennifer",
"Tracy",
"Karen",
"Tammy",
"Nicole",
"Susan",
"Christine",
"Angela",
"Sandra",
"Laura",
"Tanya",
"Heather",
"Kimberly",
"Julie",
"Patricia",
"Kelly",
"Lori"
]

class Command(BaseCommand):
    help = _('Command will run `hotfix_22`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_22 "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        #----------------------------------------------------------------------#
        # ALGORITHM:
        # WE WANT TO FREEZE TIME TO THE `LAST_MODIFIED` DATETIME SO THE RECORD
        # DOES NOT LOOKED LIKE IT WAS MODIFIED. SPECIAL THANKS TO LINK:
        # https://stackoverflow.com/a/40423482
        #----------------------------------------------------------------------#

        # (1) PROCESS CUSTOMERS
        for customer in Customer.objects.filter(gender=None).iterator(chunk_size=250):
            try:
                with freeze_time(customer.last_modified):
                    self.fix_gender(customer)
            except Exception as e:
                print(e)

    def fix_gender(self, customer):
        if customer.given_name in male_names_arr:
            # print("Name:", customer.given_name, " Gender: Male")
            customer.gender = "male"
            customer.save()
            self.stdout.write(
                self.style.SUCCESS(_('Updated male customer.'))
            )
        if customer.given_name in female_names_arr:
            # print("Name:", customer.given_name, " Gender: Female")
            customer.gender = "female"
            customer.save()
            self.stdout.write(
                self.style.SUCCESS(_('Updated female customer.'))
            )
