from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.utils import *

class TestUtils(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.test_utils
    """

    def setUp(self):
        super(TestUtils, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.client

    def test_inc_range(self):
        max_i = 1
        arr = inc_range(1, 3)
        for i in arr:
            if i >= max_i:
                max_i = i
        self.assertEqual(max_i, 3)

    def test_get_random_string(self):
        value = get_random_string()
        self.assertIsNotNone(value)

    def test_generate_hash(self):
        value = "bart@overfiftyfive.com"
        hashed_value = generate_hash(value)
        self.assertIsNotNone(hashed_value)

    def test_get_unique_username_from_email(self):
        email_value = "bart@overfiftyfive.com"
        hashed_email_value = get_unique_username_from_email(email_value)

        # Ensure something was returned.
        self.assertIsNotNone(hashed_email_value)

        # Validate the 'User' fields "username" length restriction is enforced.
        self.assertTrue(len(hashed_email_value) <= 30)

    def test_int_or_none(self):
        value = int_or_none("LALALALA")
        self.assertIsNone(value)
        value = int_or_none("123")
        self.assertIsNotNone(value)
        self.assertEqual(value, 123)

    def test_float_or_none(self):
        value = float_or_none("LALALALA")
        self.assertIsNone(value)
        value = float_or_none("123.321")
        self.assertIsNotNone(value)
        self.assertEqual(value, 123.321)

    def test_reverse_with_full_domain(self):
        value = reverse_with_full_domain("o55_index_master")
        self.assertIsNone(value)
