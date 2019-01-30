# -*- coding: utf-8 -*-
import dateutil.parser
from datetime import date
from freezegun import freeze_time
from django.core.management import call_command
from django.core import mail
from django.db import transaction
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse

from tenant_foundation.models import (
    Associate, AwayLog, WorkOrder, WORK_ORDER_STATE
)


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"
TEST_ALERNATE_USER_EMAIL = "rodolfo@workery.ca"


class TestUpdateAwayLogsCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_etl.tests.commands.test_update_away_logs
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
        super(TestUpdateAwayLogsCommand, self).setUp()
        self.c = TenantClient(self.tenant)

        # Load up the dependat.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_content', TEST_SCHEMA_NAME, verbosity=0)
        call_command('populate_tenant_sample_db', TEST_SCHEMA_NAME, verbosity=0)

    def tearDown(self):
        del self.c

    def test_run(self):
        # Setup our unit tests.
        associate = Associate.objects.all().first()
        start_d = dateutil.parser.parse('2018-01-01 12:00:01')
        until_d = dateutil.parser.parse('2018-04-15 12:00:01')
        AwayLog.objects.create(
            associate = associate,
            reason = 1,
            reason_other = "Other reason",
            until_further_notice = False,
            until_date = until_d,
            start_date = start_d
        )

        # Run our test.
        freezer = freeze_time("2019-01-31 12:00:01")
        freezer.start()
        call_command('update_away_logs', verbosity=0)
        freezer.stop()

        # Verify our test.
        self.assertGreaterEqual(len(mail.outbox), 1)
