# -*- coding: utf-8 -*-
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.db import connection # Used for django tenants.
from django.db.models import Q, Prefetch
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain
from tenant_foundation.models import (
    Customer
)


logger = logging.getLogger(__name__)


#TODO: UNIT TEST


class Command(BaseCommand):
    help = _('Command takes the data in the database and modifies it for local developers machine configuration setting.')

    def handle(self, *args, **options):
        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Updating application global data ...'))
        )
        # STEP 1 - We must set the `Site` object to be the local domain we have.
        from django.contrib.sites.models import Site # https://docs.djangoproject.com/en/dev/ref/contrib/sites/#caching-the-current-site-object
        current_site = Site.objects.get_current()
        current_site.domain = settings.WORKERY_APP_HTTP_DOMAIN
        current_site.save()

        # STEP 2 - We need to iterate through all the `Franchise` objects and
        #          update their domains to be our local domain.
        domains = SharedFranchiseDomain.objects.all()
        for domain_obj in domains.all():
            domain_text = domain_obj.domain
            domain_text = domain_text.replace('workery.ca', settings.WORKERY_APP_HTTP_DOMAIN)
            domain_obj.domain = domain_text
            domain_obj.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully backfilled database.'))
        )
