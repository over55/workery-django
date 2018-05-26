# -*- coding: utf-8 -*-
import django_rq
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # HTML to TXT
from shared_foundation import constants
from shared_foundation.models import SharedUser
from shared_foundation.utils import reverse_with_full_domain


class Command(BaseCommand):
    help = _('Command will send an activation email to the user based on the username or email.')

    def add_arguments(self, parser):
        # User Account.
        parser.add_argument('email_or_username' , nargs='+', type=str)

    def handle(self, *args, **options):
        email_or_username = options['email_or_username'][0]

        try:
            for email_or_username in options['email_or_username']:
                me = SharedUser.objects.get(email__iexact=email_or_username)
                self.begin_processing(me)
        except SharedUser.DoesNotExist:
            raise CommandError(_('Account does not exist with the email or username: %s') % str(email_or_username))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(_('WORKERY: activation email was sent successfully.'))
        )

    def begin_processing(self, me):
        pr_access_code = me.generate_pr_code()

        # Generate the data.
        url = reverse_with_full_domain(
            reverse_url_id='workery_user_activation_detail',
            resolve_url_args=[pr_access_code]
        )
        web_view_url = reverse_with_full_domain(
            reverse_url_id='workery_activate_email',
            resolve_url_args=[pr_access_code]
        )
        subject = "Welcome to Over 55 Inc!"
        param = {
            'me': me,
            'url': url,
            'web_view_url': web_view_url,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('shared_auth/email/user_activation_email_view.txt', param)
        html_content = render_to_string('shared_auth/email/user_activation_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [me.email]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
