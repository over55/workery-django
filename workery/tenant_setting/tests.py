# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from shared_foundation.constants import *
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_jwt_token_and_orig_iat
from tenant_foundation.constants import *
from tenant_foundation.models import Associate, AwayLog, InsuranceRequirement, Staff, SkillSet, TaskItem, Tag, VehicleType, WorkOrderServiceFee


TEST_SCHEMA_NAME = "london"
TEST_USER_EMAIL = "bart@workery.ca"
TEST_USER_USERNAME = "bart@workery.ca"
TEST_USER_PASSWORD = "123P@$$w0rd"
TEST_USER_TEL_NUM = "123 123-1234"
TEST_USER_TEL_EX_NUM = ""
TEST_USER_CELL_NUM = "123 123-1234"


class TestTenantTeamViews(TenantTestCase):
    """
    Console:
    python manage.py test tenant_setting.tests
    """

    #------------------#
    # Setup Unit Tests #
    #------------------#

    def setup_tenant(tenant):
        """Tenant Schema"""
        tenant.schema_name = TEST_SCHEMA_NAME
        tenant.name='Over 55 (London) Inc.',
        tenant.alternate_name="Over55",
        tenant.description="Located at the Forks of the Thames in ...",
        tenant.address_country="CA",
        tenant.address_locality="London",
        tenant.address_region="Ontario",
        tenant.post_office_box_number="", # Post Offic #
        tenant.postal_code="N6H 1B4",
        tenant.street_address="78 Riverside Drive",
        tenant.street_address_extra="", # Extra line.

    @classmethod
    def setUpClass(cls):
        """
        Run at the beginning before all the unit tests run.
        """
        super().setUpClass()

    def setUp(self):
        """
        Run at the beginning of every unit test.
        """
        super(TestTenantTeamViews, self).setUp()

        # Setup our app and account.
        call_command('init_app', verbosity=0)
        call_command('populate_tenant_content', TEST_SCHEMA_NAME, verbosity=0)
        call_command('populate_tenant_sample_db', TEST_SCHEMA_NAME, verbosity=0)

        # Create the account.
        call_command(
           'create_tenant_account',
           TEST_SCHEMA_NAME,
           MANAGEMENT_GROUP_ID,
           TEST_USER_EMAIL,
           TEST_USER_PASSWORD,
           "Bart",
           "Mika",
           TEST_USER_TEL_NUM,
           TEST_USER_TEL_EX_NUM,
           TEST_USER_CELL_NUM,
           "CA",
           "London",
           "Ontario",
           "", # Post Offic #
           "N6H 1B4",
           "78 Riverside Drive",
           "", # Extra line.
           verbosity=0
        )

        # Get user and credentials.
        user = SharedUser.objects.filter(email=TEST_USER_EMAIL).first()
        token, orig_iat = get_jwt_token_and_orig_iat(user)

        # Setup our clients.
        self.anon_c = TenantClient(self.tenant)
        self.auth_c = TenantClient(self.tenant, HTTP_AUTHORIZATION='JWT {0}'.format(token))
        self.auth_c.login(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD
        )

        TaskItem.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'type_of': FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                'title': _('Completion Survey'),
                'description': _('Please call up the client and perform the satisfaction survey.'),
                'due_date': timezone.now(),
                'is_closed': False,
                'job': None,
                'ongoing_job': None,
                # 'created_by': None,
                # created_from
                # created_from_is_public
                # last_modified_by
            }
        )

    def tearDown(self):
        """
        Run at the end of every unit test.
        """
        # Delete previous data.
        SharedUser.objects.delete_all()
        TaskItem.objects.delete_all()

        # Delete our clients.
        del self.anon_c
        del self.auth_c

        # Finish teardown.
        super(TestTenantTeamViews, self).tearDown()

    def test_settings_launchpad_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_launchpad'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Settings', str(response.content))

    def test_settings_away_log_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_away_log_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Announcements', str(response.content))

    def test_settings_away_log_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_away_log_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Announcements', str(response.content))

    def test_pending_task_retrieve_and_ongoing_update_page(self):
        associate, created = Associate.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'given_name': 'Bart',
                'last_name': "Mika"
            }
        )
        away_log, created = AwayLog.objects.update_or_create(
           id=1,
           defaults={
               'id': 1,
               'associate': associate,
           }
        )
        a_url = self.tenant.reverse(reverse_id='workery_tenant_settings_away_log_update', reverse_args=[int(away_log.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Edit Away Announcement', str(response.content))

    def test_settings_away_log_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_blacklisted_clients_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Blacklisted Clients', str(response.content))

    def test_settings_tags_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_tags_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Tag', str(response.content))

    def test_settings_tags_create_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_tag_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Tag', str(response.content))

    def test_settings_tags_update_page(self):
        tag, created = Tag.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'text': 'This is a test.'
            }
        )
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_tags_update', [tag.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Tag', str(response.content))
        self.assertIn('This is a test.', str(response.content))

    def test_settings_vehicle_types_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_vehicle_types_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Tag', str(response.content))

    def test_settings_vehicle_types_create_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_vehicle_type_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Tag', str(response.content))

    def test_settings_vehicle_types_update_page(self):
        obj, created = VehicleType.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'text': 'This is a test.'
            }
        )
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_vehicle_types_update', [obj.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Vehicle Type', str(response.content))
        self.assertIn('This is a test.', str(response.content))

    def test_settings_order_service_fees_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_order_service_fees_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Order Service Fees', str(response.content))

    def test_settings_order_service_fees_create_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_order_service_fee_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Order Service Fees', str(response.content))

    def test_settings_order_service_fees_update_page(self):
        obj, created = WorkOrderServiceFee.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'title': 'This is a test.',
                'description': '-',
                'percentage': 0
            }
        )
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_order_service_fees_update', [obj.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Order Service Fees', str(response.content))
        self.assertIn('This is a test.', str(response.content))

    def test_settings_skill_set_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_skill_set_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Skill Sets', str(response.content))

    def test_settings_skill_set_create_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_skill_set_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Add Skill Set', str(response.content))

    def test_settings_skill_set_update_page(self):
        obj, created = SkillSet.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'category': 'This is a test.',
                'sub_category': '-'
            }
        )
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_skill_set_update', [obj.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Skill Set', str(response.content))
        self.assertIn('This is a test.', str(response.content))

    def test_settings_skill_set_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_insurance_requirements_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Insurance Requirements', str(response.content))

    def test_settings_skill_set_create_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_insurance_requirement_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Insurance Requirement', str(response.content))

    def test_settings_skill_set_update_page(self):
        obj, created = InsuranceRequirement.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'text': 'This is a test.'
            }
        )
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_settings_insurance_requirement_update', [obj.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Insurance Requirement', str(response.content))
        self.assertIn('This is a test.', str(response.content))
