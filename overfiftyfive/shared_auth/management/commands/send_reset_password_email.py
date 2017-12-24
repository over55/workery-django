from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.template.loader import render_to_string    # HTML to TXT
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation import models
from shared_foundation import utils


class Command(BaseCommand):
    help = 'Command will send password reset link to the user account.'

    def add_arguments(self, parser):
        parser.add_argument('email_or_username', nargs='+')

    def handle(self, *args, **options):
        try:
            for email_or_username in options['email_or_username']:
                user = User.objects.get(
                    Q(email__iexact=email_or_username) |
                    Q(username__iexact=email_or_username)
                )
                self.begin_processing(user)

        except User.DoesNotExist:
            raise CommandError(_('User does not exist with the email or username: %s') % str(email_or_username))

    def begin_processing(self, user):
        pr_access_code = None

        print("TODO: CONTINUE DEVELPOING FROM HERE.")
