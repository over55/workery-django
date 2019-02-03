# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.models import SharedUser


class Command(BaseCommand):
    help = _('Command will update the shared account.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py change_shared_account "bart@workery.ca" 1;
        """
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('is_active', nargs='+', type=int)

    def handle(self, *args, **options):
        # Get the user inputs.
        email = options['email'][0]
        is_active = options['is_active'][0]

        # Defensive Code: Prevent continuing if the email already exists.
        if not SharedUser.objects.filter(email=email).exists():
            raise CommandError(_('Email does not exist, please pick another email.'))

        # Updated user status.
        user = SharedUser.objects.filter(email=email).first()
        user.is_active = True if is_active else False
        user.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated a shared account.'))
        )
