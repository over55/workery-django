from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse


class TestSetupFixturesManagementCommand(TenantTestCase):
    def setUp(self):
        super(TestSetupFixturesManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.client

    def test_command(self):
        call_command('setup_fixtures', verbosity=0)
