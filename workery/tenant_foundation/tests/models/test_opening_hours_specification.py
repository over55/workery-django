# -*- coding: utf-8 -*-
from django.core.management import call_command
from starterkit.utils import get_unique_username_from_email
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import SharedUser
from tenant_foundation.models import *


TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestOpeningHoursSpecification(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.models.test_opening_hours_specification
    """

    def setUp(self):
        super(TestOpeningHoursSpecification, self).setUp()
        self.c = TenantClient(self.tenant)
        self.owner = SharedUser.objects.create(
            first_name="Bart",
            last_name="Mika",
            email=TEST_USER_EMAIL,
            is_active=True,
        )
        self.obj = OpeningHoursSpecification.objects.create(
            owner=self.owner,
            closes="9:00 PM",
            day_of_week="Monday",
            opens="8:00 AM"
        )

    def tearDown(self):
        del self.c
        self.obj.delete()
        self.owner.delete()
        super(TestOpeningHoursSpecification, self).tearDown()

    def test_str(self):
        self.assertIsNotNone(str(self.obj))
        self.assertIn("9:00 PM", self.obj.closes)

    def test_delete_all(self):
        OpeningHoursSpecification.objects.delete_all()
        try:
            obj = OpeningHoursSpecification.objects.get()
        except OpeningHoursSpecification.DoesNotExist:
            self.assertTrue(True)
