# -*- coding: utf-8 -*-
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import SharedFranchise
from tenant_foundation.utils import *


class TestTenantUtils(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.test_utils
    """

    def setUp(self):
        super(TestTenantUtils, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c
        super(TestTenantUtils, self).tearDown()

    def test_bool_or_none(self):
        result = bool_or_none("Bad")
        self.assertFalse(result)

        result = bool_or_none("1")
        self.assertTrue(result)

    def test_get_dt_from_toronto_timezone_ms_access_dt_string(self):
        # Test a sample.
        result = get_dt_from_toronto_timezone_ms_access_dt_string("1954-01-21, 12:00:00 AM")
        self.assertIsNotNone(result)
        self.assertIn("1954-01-21 12:00:00", str(result))

        # Test with bad text.
        result = get_dt_from_toronto_timezone_ms_access_dt_string("la la la")
        self.assertIsNone(result)

        # Test null.
        result = get_dt_from_toronto_timezone_ms_access_dt_string(None)
        self.assertIsNone(result)

    def test_get_utc_dt_from_toronto_dt_string(self):
        # Test a sample.
        result = get_utc_dt_from_toronto_dt_string("1954-01-21, 1:00:00 PM")
        self.assertIsNotNone(result)
        self.assertIn("1954-01-21 13:00:00", str(result))

        # Test with bad text.
        result = get_utc_dt_from_toronto_dt_string("la la la")
        self.assertIsNone(result)

        # Test null.
        result = get_utc_dt_from_toronto_dt_string(None)
        self.assertIsNone(result)
