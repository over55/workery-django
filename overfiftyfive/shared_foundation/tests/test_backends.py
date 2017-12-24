import json
from django.contrib.auth import authenticate
from django.core.management import call_command
from django.db.models import Q
from django.db import transaction
from django.utils import translation
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework.authtoken.models import Token
from shared_foundation import constants


TEST_USER_EMAIL = "bart@overfiftyfive.com"
TEST_USER_USERNAME = "bart@overfiftyfive.com"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestBackends(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.test_backends
    """
    @transaction.atomic
    def setUp(self):
        translation.activate('en')  # Set English
        super(TestBackends, self).setUp()
        self.c = TenantClient(self.tenant)
        call_command('init_app', verbosity=0)
        call_command(
           'create_executive_account',
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           TEST_USER_TEL_NUM,
           TEST_USER_TEL_EX_NUM,
           TEST_USER_CELL_NUM,
           verbosity=0
        )

    @transaction.atomic
    def tearDown(self):
        users = User.objects.all()
        for user in users.all():
            user.delete()
        super(TestBackends, self).tearDown()

    @transaction.atomic
    def test_authentication_with_success(self):
        auth_user = authenticate(username=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        self.assertIsNotNone(auth_user)

    @transaction.atomic
    def test_authentication_with_failure(self):
        auth_user = authenticate(username=TEST_USER_EMAIL, password="Some-bad-password")
        self.assertIsNone(auth_user)

        # Bad username plus bad password.
        auth_user = authenticate(username="Some-bad-password", password="Some-bad-password")
        self.assertIsNone(auth_user)
