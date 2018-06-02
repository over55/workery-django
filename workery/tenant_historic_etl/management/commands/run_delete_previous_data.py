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
    WorkOrder,
    # WorkOrderComment,
    Tag
)
from tenant_foundation.utils import *


"""
Run manually in console:
python manage.py run_delete_previous_data "london"
"""


class Command(BaseCommand):
    help = _('Command will delete previous data.')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Deleting previous data...'))
        )

        # Get user inputs.
        schema_name = options['schema_name'][0]

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

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Beginning deleting previous data.'))
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Customer.objects.delete_all()
        WorkOrder.objects.delete_all()
        Associate.objects.delete_all()
        Tag.objects.delete_all()
        Organization.objects.delete_all()
        Comment.objects.delete_all()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully deleted previous data.'))
        )
