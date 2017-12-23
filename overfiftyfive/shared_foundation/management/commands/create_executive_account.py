# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models.o55_user import O55User
from shared_foundation.utils import (
    get_random_string,
    get_unique_username_from_email
)


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_executive_account "bart@overfiftyfive.com" "123P@$$word" "Bart" "Mika"
        """
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)
        parser.add_argument('first_name', nargs='+', type=str)
        parser.add_argument('last_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        email = options['email'][0]
        password = options['password'][0]
        first_name = options['first_name'][0]
        last_name = options['last_name'][0]

        # Defensive Code: Prevent continuing if the email already exists.
        if O55User.objects.filter(email=email).exists():
            raise CommandError(_('Email already exists, please pick another email.'))

        # Defensive Code: Ensure the password inputted is strong.
        try:
            validate_password(password)
        except Exception as e:
            raise CommandError(e)

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

        # Attach our user to the "Executive"
        user.groups.add(constants.EXECUTIVE_GROUP_ID)

        # Generate the private access key.
        token = Token.objects.create(user=user)
