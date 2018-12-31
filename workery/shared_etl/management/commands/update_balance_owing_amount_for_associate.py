# -*- coding: utf-8 -*-
import django_rq
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.db import connection # Used for django tenants.
from django.db.models import Q
from django.db import transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # HTML to TXT

from shared_foundation.utils import int_or_none
from tenant_foundation.constants import *
from tenant_foundation.models import Associate, WorkOrder


class Command(BaseCommand):
    """
    python manage.py update_balance_owing_amount_for_associate.py "london" 6030
    """

    help = _('Command will update the `` for specific Associate inside a franchise.')

    def add_arguments(self, parser):
        # User Account.
        parser.add_argument('franchise_schema_name' , nargs='+', type=str)
        parser.add_argument('associate_id' , nargs='+', type=int)

    def handle(self, *args, **options):
        franchise_schema_name = options['franchise_schema_name'][0]
        associate_id = options['associate_id'][0]

        # Connection will set it back to our tenant.
        connection.set_schema(franchise_schema_name, True) # Switch to Tenant.

        try:
            associate = Associate.objects.get(id=int_or_none(associate_id))
            self.begin_processing(associate)

        except Associate.DoesNotExist:
            raise CommandError(_('Account does not exist with the id: %s') % str(associate_id))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(
                _('Updated associate ID #%(id)s.' % {
                    'id': str(associate_id)
                })
            )
        )

    @transaction.atomic
    def begin_processing(self, associate):
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
