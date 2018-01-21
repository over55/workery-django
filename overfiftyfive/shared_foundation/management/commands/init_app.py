# -*- coding: utf-8 -*-
import os
import sys
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.constants import *


class Command(BaseCommand):
    """
    Console:
    python manage.py init_app
    """
    help = _('Command will setup the application database to be ready for usage.')

    def handle(self, *args, **options):
        self.process_site()
        self.process_groups()
        self.stdout.write(
            self.style.SUCCESS(_('Successfully initialized application.'))
        )

    def process_site(self):
        """
        Site
        """
        current_site = Site.objects.get_current()
        current_site.domain = settings.O55_APP_HTTP_DOMAIN
        current_site.name = "Over55"
        current_site.save()

    def process_groups(self):
        """
        Group
        """
        # Executives Group
        try:
            group = Group.objects.get(id=EXECUTIVE_GROUP_ID)
            group.name = "Executives"
            group.save()
        except Exception as e:
            Group.objects.create(
                id=EXECUTIVE_GROUP_ID,
                name="Executves"
            )

        # Management Group
        try:
            group = Group.objects.get(id=MANAGEMENT_GROUP_ID)
            group.name = "Management"
            group.save()
        except Exception as e:
            Group.objects.create(
                id=MANAGEMENT_GROUP_ID,
                name="Management"
            )

        # Frontline Group
        try:
            group = Group.objects.get(id=FRONTLINE_GROUP_ID)
            group.name = "Frontline Staff"
            group.save()
        except Exception as e:
            Group.objects.create(
                id=FRONTLINE_GROUP_ID,
                name="Frontline Staff"
            )

        # Associate Group
        try:
            group = Group.objects.get(id=ASSOICATE_GROUP_ID)
            group.name = "Associates"
            group.save()
        except Exception as e:
            Group.objects.create(
                id=ASSOICATE_GROUP_ID,
                name="Associates"
            )

        # Customer Group
        try:
            group = Group.objects.get(id=CUSTOMER_GROUP_ID)
            group.name = "Customers"
            group.save()
        except Exception as e:
            Group.objects.create(
                id=CUSTOMER_GROUP_ID,
                name="Customers"
            )
