# -*- coding: utf-8 -*-
import os
import sys
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.models.franchise import SharedFranchise
from shared_foundation.models.franchise import SharedFranchiseDomain


class Command(BaseCommand):
    help = _('Loads all the data necessary to operate this application.')

    def handle(self, *args, **options):
        #create your public tenant
        public_tenant = SharedFranchise(
            schema_name='public',
            name='Over 55 (London) Inc.',
            alternate_name="Over55",
            description="Located at the Forks of the Thames in downtown London Ontario, Over 55 is a non profit charitable organization that applies business strategies to achieve philanthropic goals. The net profits realized from the services we provide will help fund our client and community programs. When you use our services and recommended products, you are helping to improve the quality of life of older adults and the elderly in our community.",
            address_country="CA",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="", # Post Offic #
            postal_code="N6H 1B4",
            street_address="78 Riverside Drive",
            street_address_extra="", # Extra line.
        )
        try:
            public_tenant.save()
        except Exception as e:
            print(e)

        # Add one or more domains for the tenant
        domain = SharedFranchiseDomain()
        domain.domain = settings.O55_APP_HTTP_DOMAIN # don't add your port or www here! on a local server you'll want to use localhost here
        domain.tenant = public_tenant
        domain.is_primary = True
        try:
            domain.save()
        except Exception as e:
            print(e)

        self.stdout.write(
            self.style.SUCCESS(_('Successfully setup public database.'))
        )

        # First call; current site fetched from database.
        from django.contrib.sites.models import Site # https://docs.djangoproject.com/en/dev/ref/contrib/sites/#caching-the-current-site-object
        current_site = Site.objects.get_current()
        current_site.domain = settings.O55_APP_HTTP_DOMAIN
        current_site.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated public.'))
        )
