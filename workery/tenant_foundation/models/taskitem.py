# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.constants import TASK_ITEM_TYPE_OF_CHOICES
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class TaskItemManager(models.Manager):
    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return TaskItem.objects.annotate(
            search=SearchVector('title', 'description', 'job__indexed_text',),
        ).filter(search=keyword)

    def delete_all(self):
        for obj in TaskItem.objects.iterator(chunk_size=500):
            obj.delete()


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


@transaction.atomic
def increment_task_item_id_number():
    """Function will generate a unique big-int."""
    last_task_item = TaskItem.objects.all().order_by('id').last();
    if last_task_item:
        return last_task_item.id + 1
    return 1


class TaskItem(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_task_items'
        ordering = ['due_date']
        verbose_name = _('TaskItem')
        verbose_name_plural = _('TaskItems')
        default_permissions = ()
        permissions = (
            ("can_get_task_items", "Can get task_items"),
            ("can_get_task_item", "Can get task_item"),
            ("can_post_task_item", "Can create task_item"),
            ("can_put_task_item", "Can update task_item"),
            ("can_delete_task_item", "Can delete task_item"),
        )

    objects = TaskItemManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_task_item_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of task item this is.'),
        choices=TASK_ITEM_TYPE_OF_CHOICES,
    )
    title = models.CharField(
        _("Title"),
        max_length=63,
        help_text=_('The title this task item.'),
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this task item.'),
    )
    due_date = models.DateField(
        _('Due Date'),
        help_text=_('The date that this task must be finished by.'),
        blank=True,
        default=get_todays_date,
        db_index=True
    )
    is_closed = models.BooleanField(
        _("Is Closed"),
        help_text=_('Was this task completed or closed?'),
        default=False,
        blank=True,
        db_index=True
    )
    was_postponed = models.BooleanField(
        _("Was postponed"),
        help_text=_('Was this task postponed?'),
        default=False,
        blank=True,
    )
    closing_reason = models.PositiveSmallIntegerField(
        _("Closing Reason"),
        help_text=_('The reason for this task was closed.'),
        blank=True,
        null=True,
        default=0,
    )
    """
    2 - Quote was too high
    3 - Job completed by someone else
    4 - Job completed by Associate
    5 - Work no longer needed
    6 - Client not satisfied with Associate
    7 - Client did work themselves
    8 - No Associate available
    9 - Work environment unsuitable
    10 - Client did not return call
    11 - Associate did not have necessary equipment
    12 - Repair not possible
    13 - Could not meet deadline
    14 - Associate did not call client
    15 - Member issue
    16 - Client billing issue
    else - {{ task_item.closing_reason_other }}
    """
    closing_reason_other = models.CharField(
        _("Closing Reason other"),
        help_text=_('A specific reason this task was closed.'),
        max_length=1024,
        blank=True,
        null=True,
        default='',
    )
    job = models.ForeignKey(
        "WorkOrder",
        help_text=_('The job order that this task is referencing.'),
        related_name="task_items",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ongoing_job = models.ForeignKey(
        "OngoingWorkOrder",
        help_text=_('The (ongoing) job order that this task is referencing.'),
        related_name="task_items",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="created_task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="last_modified_task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.id)
