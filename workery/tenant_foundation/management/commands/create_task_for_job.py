# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise,
    SharedUser
)
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    Organization,
    WorkOrder,
    # WorkOrderComment,
    Staff,
    Tag,
    TaskItem
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will create an executive account in our application.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py create_task_for_job "london" 24210 "Assign an Associate" "Please assign an associate to this job." 1 1 1
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('id', nargs='+', type=int)
        parser.add_argument('title', nargs='+', type=str)
        parser.add_argument('description', nargs='+', type=str)
        parser.add_argument('type_of', nargs='+', type=int)
        parser.add_argument('created_by_id', nargs='+', type=int)
        parser.add_argument('last_modified_by_id', nargs='+', type=int)
        # parser.add_argument('schema_name', nargs='+', type=str)
        # parser.add_argument('schema_name', nargs='+', type=str)
        # parser.add_argument('schema_name', nargs='+', type=str)
        # parser.add_argument('schema_name', nargs='+', type=str)
        # parser.add_argument('schema_name', nargs='+', type=str)
        # parser.add_argument('schema_name', nargs='+', type=str)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        order_id = int_or_none(options['id'][0])
        title = options['title'][0]
        description = options['description'][0]
        type_of = int_or_none(options['type_of'][0])
        created_by_id = int_or_none(options['created_by_id'][0])
        last_modified_by_id = int_or_none(options['last_modified_by_id'][0])

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        try:
            created_by = SharedUser.objects.get(id=created_by_id)
            last_modified_by = SharedUser.objects.get(id=last_modified_by_id)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('User ID # does not exist.'))

        # Connection will set it back to our tenant.
        connection.set_schema(schema_name, True) # Switch to Tenant.

        # Defensive Code: Prevent continuing if the ID# does not exist.
        if not WorkOrder.objects.filter(id=order_id).exists():
            raise CommandError(_('ID # does not exists, please pick another ID #.'))

        # Create the user.
        work_order = WorkOrder.objects.get(id=order_id)

        # Created tasks.
        task = TaskItem.objects.create(
            created_by=created_by,
            last_modified_by=last_modified_by,
            type_of = type_of,
            due_date = work_order.start_date,
            is_closed = False,
            job = work_order,
            title = title,
            description = description
        )

        self.stdout.write(self.style.SUCCESS(_('Created "TaskItem" object.')))

        work_order.latest_pending_task = task
        work_order.save()

        self.stdout.write(self.style.SUCCESS(_('Updated "WorkOrder" object.')))

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully created task in tenant account.'))
        )
