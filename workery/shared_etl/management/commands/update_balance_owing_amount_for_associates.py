# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from dateutil import tz
from decimal import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command

from shared_foundation.utils import int_or_none
from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from tenant_foundation.constants import *
from tenant_foundation.models import Associate, WorkOrder


class Command(BaseCommand): #TODO: UNIT TEST
    """
    python manage.py update_balance_owing_amount_for_associates
    """
    help = _('ETL will iterate through all associates in all tenants and update balance owing amount.')

    def handle(self, *args, **options):
        franchises = SharedFranchise.objects.filter(
            ~Q(schema_name="public") &
            ~Q(schema_name="test")
        )
        for franchise in franchises.all():
            # Connection needs first to be at the public schema, as this is where
            # the database needs to be set before creating a new tenant. If this is
            # not done then django-tenants will raise a "Can't create tenant outside
            # the public schema." error.
            connection.set_schema_to_public() # Switch to Public.

            # Connection will set it back to our tenant.
            connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

            # Run the command which exists in the franchise.
            self.run_update_associate_balance_owing_amount_for_franchise(franchise)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all associates.'))
        )

    @transaction.atomic
    def run_update_associate_balance_owing_amount_for_franchise(self, franchise):
        """
        Function iterates through all the associates inside a `Franchise` and
        compute each associates `WorkOrder`.
        """
        for associate in Associate.objects.order_by('id').iterator():
            was_updated = self.update_associate(associate)
            if was_updated:
                self.stdout.write(
                    self.style.SUCCESS(
                        _('Updated associate ID #%(id)s.' % {
                            'id': str(associate.id)
                        })
                    )
                )

    def update_associate(self, associate):
        total_balance = 0.00
        was_balanced = False
        for job in WorkOrder.objects.filter(associate=associate).order_by('-id').iterator():
            total_balance += job.invoice_balance_owing_amount
            was_balanced = True

        # Update record.
        associate.balance_owing_amount = total_balance
        associate.save()

        # Return status.
        return was_balanced
