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
from tenant_foundation.models import Associate


TEST_USER_EMAIL = "acclarke@verfiftyfive.com"


class TestTenantAssociateModel(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.models.test_associates
    """

    def setUp(self):
        super(TestTenantAssociateModel, self).setUp()
        self.c = TenantClient(self.tenant)
        self.user = O55User.objects.create(
            first_name="Aurthor",
            last_name="Clarke",
            email=TEST_USER_EMAIL,
            username=get_unique_username_from_email(TEST_USER_EMAIL),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.associate = Associate.objects.create(
            user=self.user,
            given_name="Aurthor",
            last_name="Clarke",
            middle_name="C."
        )

    def tearDown(self):
        Associate.objects.delete_all()
        del self.c
        self.associate = None
        self.user.delete()
        super(TestTenantAssociateModel, self).tearDown()

    def test_str(self):
        # CASE 1 OF 2:
        value = str(self.associate)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor C. Clarke", value)

        # CASE 2 OF 2:
        self.associate.middle_name = None
        value = str(self.associate)
        self.assertIsNotNone(value)
        self.assertEqual("Aurthor Clarke", value)
