# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from shared_foundation.models import O55User
from shared_foundation.utils import *
from tenant_foundation.models import Organization


TEST_USER_EMAIL = "acclarke@verfiftyfive.com"


class TestTenantOrganizationModel(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.models.test_organization
    """

    def setUp(self):
        super(TestTenantOrganizationModel, self).setUp()
        self.c = TenantClient(self.tenant)
        self.organization = Organization.objects.create(
            name="Over55",
            alternate_name="Over55 (London) Inc.",
            address_country="CA",
            address_locality="London",
            address_region="Ontario",
            post_office_box_number="", # Post Offic #
            postal_code="N6H 1B4",
            street_address="78 Riverside Drive",
            street_address_extra="", # Extra line.
        )

    def tearDown(self):
        Organization.objects.delete_all()
        del self.c
        super(TestTenantOrganizationModel, self).tearDown()

    def test_str(self):
        # CASE 1 OF 2:
        value = str(self.organization)
        self.assertIsNotNone(value)
        self.assertEqual("Over55", value)

        # CASE 2 OF 2:
        self.organization.name = None
        self.organization.save()
        value = str(self.organization)
        self.assertIsNotNone(value)
        self.assertEqual('None', value)
