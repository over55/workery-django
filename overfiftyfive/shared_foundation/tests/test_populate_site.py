# -*- coding: utf-8 -*-
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse


class TestPopulateSiteManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.test_populate_site
    """

    def setUp(self):
        super(TestPopulateSiteManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c

    def test_command(self):
        call_command('populate_site', verbosity=0)
