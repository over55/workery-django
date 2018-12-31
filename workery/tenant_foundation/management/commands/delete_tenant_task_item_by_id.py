# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _


from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise,
    SharedUser
)
from shared_foundation.utils import int_or_none
from tenant_foundation.models import TaskItem
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will delete a task by inputted tenant name and task ID.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py delete_tenant_task_item_by_id "london" 1254
        """
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        # Get the user inputs.
        schema_name = options['schema_name'][0]
        task_id = int_or_none(options['id'][0])

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(schema_name, True) # Switch to Tenant.

        # Defensive Code: Prevent continuing if the ID# does not exist.
        if not TaskItem.objects.filter(id=task_id).exists():
            raise CommandError(_('ID # does not exists, please pick another ID #.'))

        # Create the user.
        task = TaskItem.objects.get(id=task_id)
        task.delete()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully deleted a task.'))
        )
