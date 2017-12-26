from django.core.management import call_command
from starterkit.utils import get_unique_username_from_email
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from shared_foundation.models import *


class TestModelStringFunc(TenantTestCase):
    """
    Console:
    python manage.py test shared_foundation.tests.test_model_str_func
    """

    def setUp(self):
        super(TestModelStringFunc, self).setUp()
        self.c = TenantClient(self.tenant)

    def tearDown(self):
        del self.client

    def test_o55_user(self):
        user = O55User.objects.create(
            first_name="Bart",
            last_name="Mika",
            email="bart@overfiftyfive.com",
            username=get_unique_username_from_email("bart@overfiftyfive.com"),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.assertIsNotNone(user)
        value = str(user)
        self.assertIn("bart@overfiftyfive.com", value)

    def test_franchise(self):
        #create your public tenant
        public_tenant = SharedFranchise(
            schema_name='public',
            name='Over 55 (London) Inc.',
        )
        self.assertIsNotNone(public_tenant)
        value = str(public_tenant)
        self.assertIn("Over 55 (London) Inc.", value)
