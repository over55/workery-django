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
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_25`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_25 "london"
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

        self.stdout.write(
            self.style.SUCCESS(_('Starting updating associates...'))
        )
        for associate in Associate.objects.all().iterator(chunk_size=250):
            try:
                with freeze_time(associate.last_modified):
                    associate.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated associate.'))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Starting updating clients...'))
        )
        for client in Customer.objects.all().iterator(chunk_size=250):
            try:
                with freeze_time(client.last_modified):
                    client.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated client.'))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Starting updating partners...'))
        )
        for partner in Partner.objects.all().iterator(chunk_size=250):
            try:
                with freeze_time(partner.last_modified):
                    partner.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated partner.'))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Starting updating staff...'))
        )
        for staff in Staff.objects.all().iterator(chunk_size=250):
            try:
                with freeze_time(staff.last_modified):
                    staff.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated staff.'))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Starting updating orders...'))
        )
        for order in WorkOrder.objects.all().iterator(chunk_size=250):
            try:
                with freeze_time(order.last_modified):
                    order.save()
                    self.stdout.write(
                        self.style.SUCCESS(_('Updated order.'))
                    )
            except Exception as e:
                print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all unassigned associates.'))
        )
