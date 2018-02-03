# -*- coding: utf-8 -*-
from django.core.management import call_command
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation import constants
from shared_foundation.models import O55User
from tenant_foundation.models import SkillSet


TEST_SCHEMA_NAME = "london_test"
TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestPopulateTenantContentManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.commands.test_populate_tenant_content
    """
    #------------------#
    # Setup Unit Tests #
    #------------------#

    def setup_tenant(tenant):
        """Tenant Schema"""
        tenant.schema_name = TEST_SCHEMA_NAME
        tenant.name='Over 55 (London) Inc.',
        tenant.alternate_name="Over55",
        tenant.description="Located at the Forks of the Thames in ...",
        tenant.address_country="CA",
        tenant.address_locality="London",
        tenant.address_region="Ontario",
        tenant.post_office_box_number="", # Post Offic #
        tenant.postal_code="N6H 1B4",
        tenant.street_address="78 Riverside Drive",
        tenant.street_address_extra="", # Extra line.

    def setUp(self):
        super(TestPopulateTenantContentManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)

    def tearDown(self):
        # users = O55User.objects.all()
        # for user in users.all():
        #     user.delete()
        del self.c
        super(TestPopulateTenantContentManagementCommand, self).tearDown()

    def test_command_with_success(self):
        call_command(
           'populate_tenant_content',
           TEST_SCHEMA_NAME,
           verbosity=0
        )

    def test_command_with_missing_tenant_error(self):
        try:
            call_command(
               'populate_tenant_content',
               'avalon',
               verbosity=0
            )
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertIn("Franchise does not exist!", str(e))
