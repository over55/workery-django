from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.template.loader import render_to_string    # HTML to TXT
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *
from shared_foundation.models import SharedMe
from shared_foundation.utils import reverse_with_full_domain


class Command(BaseCommand):
    help = 'Command will send password reset link to the user account.'

    def add_arguments(self, parser):
        parser.add_argument('email_or_username', nargs='+')

    def handle(self, *args, **options):
        try:
            for email_or_username in options['email_or_username']:
                me = SharedMe.objects.get(
                    Q(user__email__iexact=email_or_username) |
                    Q(user__username__iexact=email_or_username)
                )
                self.begin_processing(me)

        except SharedMe.DoesNotExist:
            raise CommandError(_('Account does not exist with the email or username: %s') % str(email_or_username))

    def begin_processing(self, me):
        pr_access_code = me.generate_pr_code()


        
