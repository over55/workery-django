# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.models import SharedUser


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_shared_account "bart@workery.ca" "123password" "Bart" "Mika";
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

        # Attach our user to the "Executive"
        user.groups.add(constants.EXECUTIVE_GROUP_ID)

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully created a shared account.'))
        )
