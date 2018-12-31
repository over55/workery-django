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

from shared_foundation import constants
from shared_foundation.models import SharedFranchise
from tenant_foundation.constants import *
from tenant_foundation.models import Associate, WorkOrder, AwayLog


class Command(BaseCommand):
    """
    python manage.py send_update_away_log "london" 60
    """

    help = _('-')

    def add_arguments(self, parser):
        # User Account.
        parser.add_argument('franchise_schema_name' , nargs='+', type=str)
        parser.add_argument('away_id' , nargs='+', type=int)

    def handle(self, *args, **options):
        franchise_schema_name = options['franchise_schema_name'][0]
        away_id = options['away_id'][0]

        # Connection will set it back to our tenant.
        connection.set_schema(franchise_schema_name, True) # Switch to Tenant.

        try:
            franchise = SharedFranchise.objects.get(schema_name=franchise_schema_name)
            away_log = AwayLog.objects.get(id=int(away_id))
            self.begin_processing(franchise, away_log)

        except AwayLog.DoesNotExist:
            raise CommandError(_('Account does not exist with the id: %s') % str(away_log))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(
                _('Emailed about Away Log ID #%(id)s.' % {
                    'id': str(away_id)
                })
            )
        )

    @transaction.atomic
    def begin_processing(self, franchise, away_log):
        tenant_todays_date = franchise.get_todays_date_plus_days()

        subject = "AwayLog Update"
        param = {
            'tenant_todays_date': tenant_todays_date,
            'away_log': away_log,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('shared_etl/email/away_log_email_view.txt', param)
        # html_content = render_to_string('shared_auth/email/user_activation_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [settings.DEFAULT_TO_EMAIL]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        # msg.attach_alternative(html_content, "text/html")
        msg.send()
