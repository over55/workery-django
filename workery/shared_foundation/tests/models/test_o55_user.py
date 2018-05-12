# -*- coding: utf-8 -*-
from django.core.management import call_command
from starterkit.utils import get_unique_username_from_email
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import *


TEST_USER_EMAIL = "bart@workery.com"
TEST_USER_USERNAME = "bart@workery.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestOver55User(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.models.test_o55_user
    """

    def setUp(self):
        super(TestOver55User, self).setUp()
        self.c = TenantClient(self.tenant)
        self.user = SharedUser.objects.create(
            first_name="Bart",
            last_name="Mika",
            email=TEST_USER_EMAIL,
            is_active=True,
        )

    def tearDown(self):
        del self.c
        self.user.delete()
        super(TestOver55User, self).tearDown()

    def test_str(self):
        self.assertIsNotNone(str(self.user))
        self.assertIn(TEST_USER_EMAIL, str(self.user))
