# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from freezegun import freeze_time
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.models import (
    Associate,
    Comment,
    Customer,
    Organization,
    OngoingWorkOrder,
    ONGOING_WORK_ORDER_STATE,
    WorkOrder,
    WORK_ORDER_STATE,
    WorkOrderComment,
    Staff,
    Tag,
    TaskItem,
    Partner
)
from tenant_foundation.utils import *
from tenant_foundation.constants import FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class Command(BaseCommand):
    """
    Run manually in console:
    python manage.py process_paid_order "london" 123456 1 "127.0.0.1" 1
    """
    help = _('Command will process a work order which is paid. Command can only be run on paid orders.')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='?', type=str)
        parser.add_argument('work_order_id', nargs='?', type=int)
        parser.add_argument('user_id', nargs='?', type=int)
        parser.add_argument('from_ip', nargs='?', type=str)
        parser.add_argument('from_ip_is_public', nargs='?', type=int)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name']
        work_order_id = options['work_order_id']
        user_id = options['user_id']
        from_ip = options['from_ip']
        from_ip_is_public = options['from_ip_is_public']

        # print("INPUT")
        # print(schema_name)
        # print(work_order_id)
        # print(user_id)
        # print(from_ip)
        # print(from_ip_is_public)

        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        try:
            order = WorkOrder.objects.get(id=work_order_id)
            if order.state == WORK_ORDER_STATE.COMPLETED_AND_PAID:
                self.process(order, user_id, from_ip, from_ip_is_public)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

    @transaction.atomic
    def process(self, order, user_id, from_ip, from_ip_is_public):
        #-----------------------------------------------------------------------
        # We are going to go through all the tasks, belonging to this order,
        # which are non-survey taks and close them.
        #-----------------------------------------------------------------------

        non_survey_tasks = TaskItem.objects.filter(
            ~Q(type_of=FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID) &
            Q(job=order) &
            Q(is_closed=False)
        )
        for non_survey_task in non_survey_tasks:
            non_survey_task.is_closed = True
            non_survey_task.last_modified_by_id = user_id
            non_survey_task.last_modified_from = from_ip
            non_survey_task.created_from_is_public = from_ip_is_public
            non_survey_task.save()

            # For debugging purposes.
            self.stdout.write(
                self.style.SUCCESS(_('Successfully closed non-survey task id #%(id)s.') % {
                    'id': str(non_survey_task.id)
                })
            )

        #-----------------------------------------------------------------------
        # We will count how many survey type of tasks we have, belonging to this
        # order, and if there is zero survey tasks then we must create it here.
        #-----------------------------------------------------------------------

        survey_tasks_count = TaskItem.objects.filter(
            Q(type_of=FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID) &
            Q(job=order),
        ).count()

        if survey_tasks_count == 0:
            # Generate our task title.
            title = _('Survey')

            # Rational: We want to ask the customer after 7 days AFTER the completion date.
            meeting_date = get_todays_date_plus_days(7)

            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID,
                title = title,
                description = _('Please call client and review the associate.'),
                due_date = meeting_date,
                is_closed = False,
                job = order,
                created_by_id = user_id,
                created_from = from_ip,
                created_from_is_public = from_ip_is_public,
                last_modified_by_id = user_id,
                last_modified_from = from_ip,
                last_modified_from_is_public = from_ip_is_public,
            )

            # For debugging purposes.
            self.stdout.write(
                self.style.SUCCESS(_('Successfully created survey task ID #%(id)s.') %{
                    'id': str(next_task_item.id)
                })
            )

            # Update the job.
            order.latest_pending_task = next_task_item
            order.last_modified_by_id = user_id
            order.last_modified_from = from_ip
            order.last_modified_from_is_public = from_ip_is_public
            order.save()
