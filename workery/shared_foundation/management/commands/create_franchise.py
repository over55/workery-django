# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from django_rq import get_queue, get_worker
from shared_foundation import constants
from shared_foundation.models import (
    SharedFranchise,
    SharedFranchiseDomain,
    SharedUser
)


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_franchise "london" "Over55" "Over55 (London) Inc." "Located at the Forks of the Thames in downtown London Ontario, Over 55 is a non profit charitable organization that applies business strategies to achieve philanthropic goals. The net profits realized from the services we provide will help fund our client and community programs. When you use our services and recommended products, you are helping to improve the quality of life of older adults and the elderly in our community." "CA" "London" "Ontario" "" "N6H 1B4" "78 Riverside Drive" ""
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('name', nargs='+', type=str)
        parser.add_argument('alternate_name', nargs='+', type=str)
        parser.add_argument('description', nargs='+', type=str)
        parser.add_argument('address_country', nargs='+', type=str)
        parser.add_argument('address_locality', nargs='+', type=str)
        parser.add_argument('address_region', nargs='+', type=str)
        parser.add_argument('post_office_box_number', nargs='+', type=str)
        parser.add_argument('postal_code', nargs='+', type=str)
        parser.add_argument('street_address', nargs='+', type=str)
        parser.add_argument('street_address_extra', nargs='+', type=str)
        parser.add_argument('timezone_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        name = options['name'][0]
        alternate_name = options['alternate_name'][0]
        description = options['description'][0]
        address_country = options['address_country'][0]
        address_locality = options['address_locality'][0]
        address_region = options['address_region'][0]
        post_office_box_number = options['post_office_box_number'][0]
        postal_code = options['postal_code'][0]
        street_address = options['street_address'][0]
        street_address_extra = options['street_address_extra'][0]
        timezone_name = options['timezone_name'][0]

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Check to confirm that we already do not have a `Franchise` with this
        # name in our database.
        franchise_does_exist = SharedFranchise.objects.filter(schema_name=schema_name).exists()
        if franchise_does_exist:
            raise CommandError(_('Franchise already exists!'))

        # Create our tenant.
        self.begin_processing(schema_name, name, alternate_name, description,
                             address_country, address_locality, address_region,
                             post_office_box_number, postal_code, street_address,
                             street_address_extra, timezone_name)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully setup franchise.'))
        )

    def begin_processing(self, schema_name, name, alternate_name, description,
                         address_country, address_locality, address_region,
                         post_office_box_number, postal_code, street_address,
                         street_address_extra, timezone_name):
        """
        Functin will create a new tenant based on the parameters.
        """

        # Create your tenant
        tenant = SharedFranchise(
            schema_name=schema_name,
            name=name,
            alternate_name=alternate_name,
            description=description,
            address_country=address_country,
            address_locality=address_locality,
            address_region=address_region,
            post_office_box_number=post_office_box_number,
            postal_code=postal_code,
            street_address=street_address,
            street_address_extra=street_address_extra,
            timezone_name=timezone_name
        )
        tenant.save()

        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705

        # Add one or more domains for the tenant
        domain = SharedFranchiseDomain()
        domain.domain = settings.WORKERY_APP_HTTP_DOMAIN
        domain.domain = tenant.schema_name + '.' + settings.WORKERY_APP_HTTP_DOMAIN
        domain.tenant = tenant
        domain.is_primary = False
        domain.save()

        get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705

        # Populate our new organization tenant with post-creation data.
        call_command('populate_tenant_content', schema_name, verbosity=0)
