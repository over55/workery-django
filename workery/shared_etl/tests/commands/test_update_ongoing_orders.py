# -*- coding: utf-8 -*-
from freezegun import freeze_time
from django.core.management import call_command
from django.db import transaction
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse

from shared_foundation.models.user import SharedUser


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"
TEST_ALERNATE_USER_EMAIL = "rodolfo@workery.ca"


class TestUpdateOngoingOrdersCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_etl.tests.commands.test_update_ongoing_orders
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

    @transaction.atomic
    def setUp(self):
        super(TestUpdateOngoingOrdersCommand, self).setUp()
        self.c = TenantClient(self.tenant)

        # Load up the dependat.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_content', TEST_SCHEMA_NAME, verbosity=0)
        call_command('populate_tenant_sample_db', TEST_SCHEMA_NAME, verbosity=0)

    def tearDown(self):
        del self.c

    @transaction.atomic
    def test_first_day_of_month(self):
        """
        Unit test confirms the command works for the first day of the month.
        """
        freezer = freeze_time("2019-02-01 12:00:01")
        freezer.start()
        call_command('update_ongoing_orders', verbosity=0)
        freezer.stop()

    @transaction.atomic
    def test_last_day_of_month(self):
        """
        Unit test confirms the command works for the last day of the month.
        """
        freezer = freeze_time("2019-01-31 12:00:01")
        freezer.start()
        call_command('update_ongoing_orders', verbosity=0)
        freezer.stop()

    # @transaction.atomic
    # def test_other_days_of_the_month(self):
    #     """
    #     Unit test confirms the command works for the other days of the month.
    #     """
    #     freezer = freeze_time("2019-01-30 12:00:01")
    #     freezer.start()
    #     call_command('update_ongoing_orders', verbosity=0)
    #     freezer.stop()
    #
    #     freezer = freeze_time("2019-02-02 12:00:01")
    #     freezer.start()
    #     call_command('update_ongoing_orders', verbosity=0)
    #     freezer.stop()
