# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from dateutil import tz, relativedelta
from decimal import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.db import connection # Used for django tenants.
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # EMAILER: HTML to TXT
from django_tenants.utils import tenant_context

from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from shared_foundation.utils import get_end_of_date_for_this_dt, get_first_date_for_this_dt
from tenant_foundation import constants
from tenant_foundation.models import ACTIVITY_SHEET_ITEM_STATE
from tenant_foundation.models import ActivitySheetItem
from tenant_foundation.models.work_order import WORK_ORDER_STATE
from tenant_foundation.models.taskitem import TaskItem
from tenant_foundation.models.work_order import WorkOrder
from tenant_foundation.models.ongoing_work_order import ONGOING_WORK_ORDER_STATE
from tenant_foundation.models.ongoing_work_order import OngoingWorkOrder
from tenant_foundation.models import Associate, AssociateComment, AwayLog, Comment, Staff


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class Command(BaseCommand): #TODO: UNIT TEST
    """
    Description:
    Command will iterate through all the associates (which are active) and
    perform the following:

    (1) At first of month, check to see if the associate has:
    (2) Expired policy check
    (3) Expired insurance
    (4) And associate sets become set "away" if (2) or (3) is true.

    Example:
    python manage.py update_expired_associates
    """
    help = _('ETL will iterate through all associates in all tenants to see if we need to set associates as expired.')

    def handle(self, *args, **options):
        franchises = SharedFranchise.objects.filter(
            ~Q(schema_name="public") &
            ~Q(schema_name="test")
        )

        # Iterate through all the franchise schemas and perform our operations
        # limited to the specific operation.
        for franchise in franchises.all():
            with tenant_context(franchise):
                self.run_update_expired_associates_for_franchise(franchise)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated all ongoing job orders.'))
        )

    def send_staff_an_email(self, staff, type_of, associate, now_dt, now_d):
        subject = None
        param = None
        reason = None

        if type_of == "commercial-insurance-expiry":
            subject = "WORKERY: Associate insurance expiry"
            reason = "commercial insurance has expired"
        elif type_of == "police-check-expiry":
            subject = "WORKERY: Associate police check has expired"
            reason = "police check has expired"

        param = {
            'tenant_todays_date': now_d,
            'associate': associate,
            'reason': reason,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('shared_etl/email/update_expired_associates.txt', param)
        # html_content = render_to_string('shared_etl/email/update_expired_associates.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [staff.email,]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        # msg.attach_alternative(html_content, "text/html")
        msg.send()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('Sent email to: %(email)s.')%{
                'email': str(staff.email)
            })
        )

    def run_update_expired_associates_for_franchise(self, franchise):
        # Get the current date for this particular franchise.
        now_dt = franchise.get_todays_date_plus_days()
        now_d = now_dt.date()

        # Fetch all the active assocaites in the franchise.
        associates = Associate.objects.filter(
            owner__is_active=True
        ).prefetch_related(
            'owner'
        ).order_by(
            'last_name',
            'given_name',
        );

        # Iterate through all the associates in the franchise.
        for associate in associates.iterator():
            away_log_count = associate.away_logs.filter(was_deleted=False).count()
            if away_log_count > 0:
                self.stdout.write(
                    self.style.WARNING(_('Skipping associate # %(id)s.')%{
                        'id': str(associate.id),
                    })
                )
            else:
                self.run_update_expired_associate(associate, now_dt, now_d)

    def process_associate_for_expired_police_check(self, associate, now_dt, now_d, police_check_d):
        """
        Function called when an associate needs to be be put on the away
        list if their policy check has expired.
        """
        # STEP 1: Create `AwayLog` object.
        log = AwayLog.objects.create(
            associate=associate,
            reason=5, # Policy Check Expired
            reason_other=None,
            until_further_notice=True,
            start_date=now_dt,
        )

        # STEP 2: Create comments.
        comment_obj = Comment.objects.create(
            text="Police check expired"
        )
        associate_comment = AssociateComment.objects.create(
            about=associate,
            comment=comment_obj,
        )

        # STEP 3: Update the associate to have the `AwayLog` object assigned to it.
        associate.away_log = log
        associate.save()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('Created away-log for associate # %(id)s for police check expiry at %(dt)s.')%{
                'id': str(associate.id),
                'dt': str(police_check_d)
            })
        )

        # STEP 4:
        # Fetch the franchise management staff and send a notification
        # email informing them that an associate has expired commercial
        # insurance.
        management_staffs = Staff.objects.filter_by_active_management_group()
        for staff in management_staffs.iterator():
            self.send_staff_an_email(staff, "police-check-expiry", associate, now_dt, now_d)

    def process_associate_for_commercial_insurance_expiry(self, associate, now_dt, now_d, commercial_insurance_expiry_d):
        """
        Function called when an associate needs to be be put on the away
        list if their commercial check has expired.
        """
        # STEP 1: Create `AwayLog` object.
        log = AwayLog.objects.create(
            associate=associate,
            reason=4, # Commercial Insurance Expiry.
            reason_other=None,
            until_further_notice=True,
            start_date=now_dt,
        )

        # STEP 2: Create comments.
        comment_obj = Comment.objects.create(
            text="Commercial insurance expired"
        )
        associate_comment = AssociateComment.objects.create(
            about=associate,
            comment=comment_obj,
        )

        # STEP 3: Update the associate to have the `AwayLog` object assigned to it.
        associate.away_log = log
        associate.save()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('Created away-log for associate # %(id)s for commercial insurance expiry at %(dt)s.')%{
                'id': str(associate.id),
                'dt': str(commercial_insurance_expiry_d)
            })
        )

        # STEP 4:
        # Fetch the franchise management staff and send a notification
        # email informing them that an associate has expired commercial
        # insurance.
        management_staffs = Staff.objects.filter_by_active_management_group()
        for staff in management_staffs.iterator():
            self.send_staff_an_email(staff, "commercial-insurance-expiry", associate, now_dt, now_d)

    def run_update_expired_associate(self, associate, now_dt, now_d):
        # Insurance expired.
        commercial_insurance_expiry_d = associate.commercial_insurance_expiry_date
        if commercial_insurance_expiry_d:
            if commercial_insurance_expiry_d <= now_d:
                self.process_associate_for_commercial_insurance_expiry(associate, now_dt, now_d, commercial_insurance_expiry_d)

        # Policy check expired.
        police_check_d = associate.police_check

        if police_check_d:
            # CASE 1 OF 3: POLICE CHECK HAS EXPIRED.
            if police_check_d <= now_d:
                self.stdout.write(
                    self.style.WARNING(_('Associate #%(id)s policy check of %(dt) has expired as of today %(dt_fin)s.')%{
                        'id': str(associate.id),
                        'dt': str(police_check_d),
                        'dt_fin': str(now_d)
                    })
                )
                self.process_associate_for_expired_police_check(associate, now_dt, now_d, police_check_d)

            # CASE 2 OF 3: POLICE CHECK HAS NOT EXPIRED.
            else:
                self.stdout.write(
                    self.style.SUCCESS(_('Associate #%(id)s has police check which has not expired.')%{
                        'id': str(associate.id)
                    })
                )
        # CASE 3 OF 3: NO POLICE CHECK SPECIFIED! (VERY BAD!)
        else:
            self.stdout.write(
                self.style.ERROR(_('Associate #%(id)s is missing a policy check!')%{
                    'id': str(associate.id),
                })
            )
            self.process_associate_for_expired_police_check(associate, now_dt, now_d, police_check_d)
