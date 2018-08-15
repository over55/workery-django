# -*- coding: utf-8 -*-
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import SharedFranchise


class TestCreateFranchiseTenantManagementCommand(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.commands.test_create_franchise
    """

    def setUp(self):
        super(TestCreateFranchiseTenantManagementCommand, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.c

    def test_command(self):
        # Case 1 of 2: Unique.
        call_command(
            "create_franchise",
            "london_test",
            "Over55",
            "Over55 (London) Inc.",
            "Located at the Forks of the Thames in downtown London Ontario, Over 55 is a non profit charitable organization that applies business strategies to achieve philanthropic goals. The net profits realized from the services we provide will help fund our client and community programs. When you use our services and recommended products, you are helping to improve the quality of life of older adults and the elderly in our community.",
            "CA",
            "London",
            "Ontario",
            "", # Post Offic #
            "N6H 1B4",
            "78 Riverside Drive",
            "", # Extra line.
            "American/Toronto",
            verbosity=0
        )

        # Case 2 of 2: Duplicate error
        try:
            call_command(
                "create_franchise",
                "london_test",
                "Over55",
                "Over55 (London) Inc.",
                "Located at the Forks of the Thames in downtown London Ontario, Over 55 is a non profit charitable organization that applies business strategies to achieve philanthropic goals. The net profits realized from the services we provide will help fund our client and community programs. When you use our services and recommended products, you are helping to improve the quality of life of older adults and the elderly in our community.",
                "CA",
                "London",
                "Ontario",
                "", # Post Offic #
                "N6H 1B4",
                "78 Riverside Drive",
                "", # Extra line.
                "American/Toronto",
                verbosity=0
            )
        except Exception as e:
            self.assertIsNotNone(e)

        # Delete.
        franchise = SharedFranchise.objects.get(schema_name="london_test")
        franchise.delete()
