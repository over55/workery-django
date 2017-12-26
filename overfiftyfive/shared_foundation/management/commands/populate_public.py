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
