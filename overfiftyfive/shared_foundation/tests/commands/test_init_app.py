# -*- coding: utf-8 -*-
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse


class TestInitAppManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.commands.test_init_app
    """

    def setUp(self):
        super(TestInitAppManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c

    def test_command(self):
        # CASE 1 of 2: Run the application for the first time.
        call_command('init_app', verbosity=0)

        # CASE 2 of 2: Run the application for the second time and confirm
        #              that no errors occure.
        call_command('init_app', verbosity=0)
