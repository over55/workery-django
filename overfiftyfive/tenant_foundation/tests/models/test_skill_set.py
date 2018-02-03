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
from tenant_foundation.models import SkillSet


TEST_USER_EMAIL = "acclarke@verfiftyfive.com"


class TestTenantSkillSetModel(TenantTestCase):
    """
    Console:
    python manage.py test tenant_foundation.tests.models.test_skill_set
    """

    def setUp(self):
        super(TestTenantSkillSetModel, self).setUp()
        self.skill_set = SkillSet.objects.create(
           category="Carpentry",
           sub_category="Carpentry",
           insurance_requirement="General Liability $2M"
        )

    def tearDown(self):
        SkillSet.objects.delete_all()
        self.skill_set = None
        super(TestTenantSkillSetModel, self).tearDown()

    def test_str(self):
        # CASE 1 OF 2:
        value = str(self.skill_set)
        self.assertIsNotNone(value)
        self.assertEqual("Carpentry Carpentry", value)
