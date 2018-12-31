# -*- coding: utf-8 -*-
from datetime import timedelta
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.utils import timezone
from shared_foundation import constants
from shared_foundation.models import SharedUser, SharedUser


class TestSendActivationEmail(TenantTestCase):
    """
    Class used to test the email views.

    Console:
    python manage.py test shared_auth.tests.test_send_activation_email
    """

    def setUp(self):
        super(TestSendActivationEmail, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)
        call_command(
           'create_shared_account',
           'bart+test2@workery.ca',
           '123password',
           "Bart",
           "Mika",
           verbosity=0
        )

    def test_run(self):
        call_command('send_activation_email', 'bart+test2@workery.ca', verbosity=0)

    def test_run_with_dne(self):
        try:
            call_command('send_activation_email', 'dev@simalam.com', verbosity=0)
        except Exception as e:
            self.assertIn("Account does not exist", str(e))
