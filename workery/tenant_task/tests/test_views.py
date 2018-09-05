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
from tenant_foundation.models import Staff, TaskItem

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
    python manage.py test tenant_task.tests.test_views
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
        user = SharedUser.objects.get()
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

    def test_unassigned_task_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_unassigned_task_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Unassigned Tasks', str(response.content))

    def test_pending_task_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_task_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Pending Tasks', str(response.content))

    def test_closed_task_list_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_closed_task_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Closed Tasks', str(response.content))

    def test_pending_task_retrieve_page(self):
        obj = TaskItem.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pending_task_retrieve', reverse_args=[int(obj.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Task', str(response.content))

    def test_pending_task_retrieve_2_page(self):
        obj = TaskItem.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pending_task_retrieve_for_activity_sheet_retrieve', reverse_args=[int(obj.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Task', str(response.content))

    def test_pending_task_retrieve_3_page(self):
        obj = TaskItem.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pending_task_retrieve_for_activity_sheet_retrieve_and_create', reverse_args=[int(obj.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Task', str(response.content))

    def test_pending_task_retrieve_4_page(self):
        obj = TaskItem.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pending_task_retrieve_for_activity_sheet_follow_up_with_associate_retrieve', reverse_args=[int(obj.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Task', str(response.content))

    def test_pending_task_retrieve_and_complete_page(self):
        obj = TaskItem.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pending_task_retrieve_and_complete_create', reverse_args=[int(obj.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Task', str(response.content))

    def test_pending_task_retrieve_and_ongoing_update_page(self):
        obj = TaskItem.objects.get()
        a_url = self.tenant.reverse(reverse_id='workery_tenant_pending_task_retrieve_and_ongoing_update_create', reverse_args=[int(obj.id)])
        response = self.auth_c.get(a_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Task', str(response.content))

    def test_search_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_task_search', ['pending']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Search', str(response.content))

    def test_search_confirmation_page(self):
        response = self.auth_c.get(self.tenant.reverse('workery_tenant_task_search_results', ['pending'])+'?keyword='+TEST_USER_EMAIL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Search', str(response.content))
