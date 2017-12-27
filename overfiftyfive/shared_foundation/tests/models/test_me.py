# -*- coding: utf-8 -*-
from django.core.management import call_command
from starterkit.utils import get_unique_username_from_email
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import *


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestMe(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.models.test_me
    """

    def setUp(self):
        super(TestMe, self).setUp()
        self.c = TenantClient(self.tenant)
        self.user = O55User.objects.create(
            first_name="Bart",
            last_name="Mika",
            email=TEST_USER_EMAIL,
            username=get_unique_username_from_email(TEST_USER_EMAIL),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.me = SharedMe.objects.create(
            user=self.user,
            tel_num='',
            tel_ext_num='',
            cell_num=''
        )

    def tearDown(self):
        del self.c
        self.me.delete()
        super(TestMe, self).tearDown()

    def test_str(self):
        self.assertIsNotNone(str(self.me))
        self.assertIn(TEST_USER_EMAIL, str(self.me))

    def test_delete_all(self):
        SharedMe.objects.delete_all()
        try:
            me = SharedMe.objects.get()
        except SharedMe.DoesNotExist:
            self.assertTrue(True)

    def test_get_by_email_or_none(self):
        # CASE 1 OF 2:
        me = SharedMe.objects.get_by_email_or_none(TEST_USER_EMAIL)
        self.assertIsNotNone(me)

        # CASE 2 OF 2:
        me = SharedMe.objects.get_by_email_or_none("trudy@overfiftyfive.com")
        self.assertIsNone(me)

    def test_get_by_user_or_none(self):
        # CASE 1 OF 2:
        me = SharedMe.objects.get_by_user_or_none(self.user)
        self.assertIsNotNone(me)

        # CASE 2 OF 2:
        me = SharedMe.objects.get_by_user_or_none(None)
        self.assertIsNone(me)
