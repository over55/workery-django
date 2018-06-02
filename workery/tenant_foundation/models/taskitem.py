# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.constants import TASK_ITEM_TYPE_OF_CHOICES
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class TaskItemManager(models.Manager):
    def delete_all(self):
        items = TaskItem.objects.all()
        for item in items.all():
            item.delete()


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
        related_name="%(app_label)s_%(class)s_job_related",
        on_delete=models.CASCADE
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.id)
