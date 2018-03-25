# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models import SharedUser


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_shared_account "bart@overfiftyfive.com" "123password" "Bart" "Mika" "123 123-1234" "" "123 123-1234" "CA" "London" "Ontario" "" "N6H 1B4" "78 Riverside Drive" ""
        """
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)
        parser.add_argument('first_name', nargs='+', type=str)
        parser.add_argument('last_name', nargs='+', type=str)
        # parser.add_argument('telephone', nargs='+', type=str)
        # parser.add_argument('telephone_extension', nargs='+', type=str)
        # parser.add_argument('mobile', nargs='+', type=str)
        # parser.add_argument('address_country', nargs='+', type=str)
        # parser.add_argument('address_locality', nargs='+', type=str)
        # parser.add_argument('address_region', nargs='+', type=str)
        # parser.add_argument('post_office_box_number', nargs='+', type=str)
        # parser.add_argument('postal_code', nargs='+', type=str)
        # parser.add_argument('street_address', nargs='+', type=str)
        # parser.add_argument('street_address_extra', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        email = options['email'][0]
        password = options['password'][0]
        first_name = options['first_name'][0]
        last_name = options['last_name'][0]

        # Defensive Code: Prevent continuing if the email already exists.
        if SharedUser.objects.filter(email=email).exists():
            raise CommandError(_('Email already exists, please pick another email.'))

        # Create the user.
        user = SharedUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=True,
            was_email_activated=True
        )

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # Generate the private access key.


        # Attach our user to the "Executive"
        user.groups.add(constants.EXECUTIVE_GROUP_ID)

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully created a shared account.'))
        )
