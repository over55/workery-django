# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedFranchiseDomain


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_franchise "london" "Over55" "Over55 (London) Inc." "Located at the Forks of the Thames in downtown London Ontario, Over 55 is a non profit charitable organization that applies business strategies to achieve philanthropic goals. The net profits realized from the services we provide will help fund our client and community programs. When you use our services and recommended products, you are helping to improve the quality of life of older adults and the elderly in our community."
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('name', nargs='+', type=str)
        parser.add_argument('alternate_name', nargs='+', type=str)
        parser.add_argument('description', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        name = options['name'][0]
        alternate_name = options['alternate_name'][0]
        description = options['description'][0]

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
        self.begin_processing(schema_name, name, alternate_name, description)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully setup tenant.'))
        )

    def begin_processing(self, schema_name, name, alternate_name, description):
        """
        Functin will create a new tenant based on the parameters.
        """

        # Create your tenant
        tenant = SharedFranchise(
            schema_name=schema_name,
            name=name,
            alternate_name=alternate_name,
            description=description
        )
        try:
            tenant.save()
        except Exception as e:
            print(e)

        # Add one or more domains for the tenant
        domain = SharedFranchiseDomain()
        domain.domain = settings.O55_APP_HTTP_DOMAIN
        domain.domain = tenant.schema_name + '.' + settings.O55_APP_HTTP_DOMAIN
        domain.tenant = tenant
        domain.is_primary = False
        try:
            domain.save()
        except Exception as e:
            print(e)
