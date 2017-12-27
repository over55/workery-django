# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models.me import SharedMe


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_executive_account "bart@overfiftyfive.com" "123password" "Bart" "Mika" "123 123-1234" "" "123 123-1234" "CA" "London" "Ontario" "" "N6H 1B4" "78 Riverside Drive" ""
        """
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)
        parser.add_argument('first_name', nargs='+', type=str)
        parser.add_argument('last_name', nargs='+', type=str)
        parser.add_argument('tel_num', nargs='+', type=str)
        parser.add_argument('tel_ext_num', nargs='+', type=str)
        parser.add_argument('cell_num', nargs='+', type=str)
        parser.add_argument('address_country', nargs='+', type=str)
        parser.add_argument('address_locality', nargs='+', type=str)
        parser.add_argument('address_region', nargs='+', type=str)
        parser.add_argument('post_office_box_number', nargs='+', type=str)
        parser.add_argument('postal_code', nargs='+', type=str)
        parser.add_argument('street_address', nargs='+', type=str)
        parser.add_argument('street_address_extra', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        email = options['email'][0]
        password = options['password'][0]
        first_name = options['first_name'][0]
        last_name = options['last_name'][0]
        tel_num = options['tel_num'][0]
        tel_ext_num = options['tel_ext_num'][0]
        cell_num = options['cell_num'][0]
        address_country = options['address_country'][0]
        address_locality = options['address_locality'][0]
        address_region = options['address_region'][0]
        post_office_box_number = options['post_office_box_number'][0]
        postal_code = options['postal_code'][0]
        street_address = options['street_address'][0]
        street_address_extra = options['street_address_extra'][0]

        # Defensive Code: Prevent continuing if the email already exists.
        if User.objects.filter(email=email).exists():
            raise CommandError(_('Email already exists, please pick another email.'))

        # Create the user.
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=get_unique_username_from_email(email),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )

        # Generate and assign the password.
        user.set_password(password)
        user.save()

        # Generate the private access key.
        token = Token.objects.create(user=user)

        # Create our profile.
        SharedMe.objects.create(
            user=user,
            tel_num=tel_num,
            tel_ext_num=tel_ext_num,
            cell_num=cell_num,
            address_country=address_country,
            address_locality=address_locality,
            address_region=address_region,
            post_office_box_number=post_office_box_number,
            postal_code=postal_code,
            street_address=street_address,
            street_address_extra=street_address_extra,
            was_email_activated=True,
        )

        # Attach our user to the "Executive"
        user.groups.add(constants.EXECUTIVE_GROUP_ID)
