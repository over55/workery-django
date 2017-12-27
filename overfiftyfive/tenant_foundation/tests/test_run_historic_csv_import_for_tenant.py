from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import SharedFranchise
from tenant_foundation.models import Staff


class TestRunHistoricCSVImportForTenantManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.test_run_historic_csv_import_for_tenant
    """

    def setUp(self):
        super(TestRunHistoricCSVImportForTenantManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c
        super(TestRunHistoricCSVImportForTenantManagementCommand, self).tearDown()

    def test_command_with_success(self):
        # CASE 1 OF 2:
        call_command("run_historic_csv_import_for_tenant", "test", "dev", verbosity=0)

        # CASE 2 OF 2:
        call_command("run_historic_csv_import_for_tenant", "test", "dev", verbosity=0)

    def test_command_with_missing_franchise(self):
        try:
            call_command("run_historic_csv_import_for_tenant", "lalalala", "dev", verbosity=0)
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Franchise does not exist!", str(e))
